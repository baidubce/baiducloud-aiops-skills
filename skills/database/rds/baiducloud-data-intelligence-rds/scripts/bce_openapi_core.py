#!/usr/bin/env python3
"""Shared IAM-signed (BCE Auth v1) HTTP client core for Baidu Cloud OpenAPI.

Read operations (GET/HEAD) run freely; mutating methods require allow_write.
Credentials come only from the environment or ~/.bce/credentials; never from CLI.

Each skill ships a thin entry script that passes a ServiceConfig describing its
endpoint and label. All signing, redaction, credential loading and request logic
lives here so a fix lands once for RDS/DTS/MongoDB/Redis alike.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import hmac
import json
import os
import re
import sys
import uuid
from typing import Callable, List, Mapping, NamedTuple, Optional
from urllib.parse import parse_qsl, quote, unquote, urlsplit

import requests

AUTHORIZATION_PREFIX = "bce-auth-v1"
DEFAULT_EXPIRATION_SECONDS = 1800
READ_METHODS = {"GET", "HEAD"}


class ServiceConfig(NamedTuple):
    """Per-service specifics injected by each skill's thin entry script."""

    label: str             # human name used in messages, e.g. "Redis"
    endpoint_env: str      # env var overriding the endpoint host
    protocol_env: str      # env var overriding http/https
    default_endpoint: str  # host used when no region/override is given
    host_template: str     # regional host, e.g. "redis.{region}.baidubce.com"
    regional: bool         # True: build host from region; False: global endpoint
    default_protocol: str = "https"  # protocol when protocol_env is unset (some services only offer http)


def _normalize(value: object, safe: str = "") -> str:
    """Percent-encode a value per RFC 3986."""
    return quote(str(value), safe=safe, encoding="utf-8", errors="strict")


def _canonical_uri(url: str) -> str:
    """Return the normalized URI path of a prepared URL."""
    return _normalize(unquote(urlsplit(url).path or "/"), safe="/-_.~")


def _canonical_query(url: str) -> str:
    """Return the sorted, normalized query string of a prepared URL."""
    pairs = [
        (_normalize(name), _normalize(value))
        for name, value in parse_qsl(urlsplit(url).query, keep_blank_values=True)
        if name.lower() != "authorization"
    ]
    pairs.sort()
    return "&".join("{}={}".format(n, v) for n, v in pairs)


def _signed_header_names(headers: Mapping[str, object]) -> List[str]:
    """Select sorted host and x-bce-* header names for signing."""
    names = {
        str(name).strip().lower()
        for name in headers
        if str(name).strip().lower() == "host"
        or str(name).strip().lower().startswith("x-bce-")
    }
    return sorted(names)


def _canonical_headers(headers: Mapping[str, object], header_names: List[str]) -> str:
    """Build the sorted, normalized canonical header block."""
    lowered = {str(n).strip().lower(): str(v).strip() for n, v in headers.items()}
    lines = ["{}:{}".format(_normalize(n), _normalize(lowered[n])) for n in header_names]
    lines.sort()
    return "\n".join(lines)


def _hmac_hex(key: object, value: str) -> str:
    """Return the lowercase hex HMAC-SHA256 of value under key."""
    key_bytes = key if isinstance(key, bytes) else str(key).encode("utf-8")
    return hmac.new(key_bytes, value.encode("utf-8"), hashlib.sha256).hexdigest()


class BceIamAuth(requests.auth.AuthBase):
    """Add BCE Auth v1 headers to a prepared request (optionally with STS token)."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        security_token: Optional[str] = None,
        expiration_seconds: int = DEFAULT_EXPIRATION_SECONDS,
        clock: Optional[Callable[[], datetime.datetime]] = None,
        request_id_factory: Optional[Callable[[], str]] = None,
    ) -> None:
        """Store credentials and deterministic injectables for signing."""
        self._access_key = access_key
        self._secret_key = secret_key
        self._security_token = security_token
        self._expiration_seconds = expiration_seconds
        self._clock = clock or datetime.datetime.utcnow
        self._request_id_factory = request_id_factory or (lambda: str(uuid.uuid1()))

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Sign one prepared request immediately before transport."""
        url = request.url or ""
        canonical_time = self._clock().strftime("%Y-%m-%dT%H:%M:%SZ")
        request.headers["host"] = urlsplit(url).netloc
        request.headers["x-bce-date"] = canonical_time
        request.headers["x-bce-request-id"] = self._request_id_factory()
        if self._security_token:
            request.headers["x-bce-security-token"] = self._security_token
        header_names = _signed_header_names(request.headers)
        auth_string = "{}/{}/{}/{}".format(
            AUTHORIZATION_PREFIX, self._access_key, canonical_time, self._expiration_seconds)
        signing_key = _hmac_hex(self._secret_key, auth_string)
        canonical_request = "\n".join((
            (request.method or "GET").upper(),
            _canonical_uri(url),
            _canonical_query(url),
            _canonical_headers(request.headers, header_names),
        ))
        signature = _hmac_hex(signing_key, canonical_request)
        request.headers["Authorization"] = "{}/{}/{}".format(
            auth_string, ";".join(header_names), signature)
        return request


# Normalized (lowercase, no separators) names of fields that must never be echoed.
_SECRET_KEYS = {
    "authorization", "accesskey", "accesskeyid", "secretaccesskey",
    "securitytoken", "xbcesecuritytoken", "secret", "password", "token",
}


def _norm_key(key: object) -> str:
    """Lowercase a key and strip separators for secret matching."""
    return str(key).lower().replace("-", "").replace("_", "")


def redact(value: object) -> object:
    """Recursively replace secret fields and presigned download URLs."""
    if value is None or isinstance(value, (int, float, bool, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            norm = _norm_key(key)
            if norm in _SECRET_KEYS:
                result[str(key)] = "<redacted>"
            elif norm == "url" or ("download" in norm and "url" in norm):
                result[str(key)] = "<temporary URL omitted>"
            else:
                result[str(key)] = redact(item)
        return result
    return str(value)


DEFAULT_CREDENTIALS_PATH = os.path.expanduser("~/.bce/credentials")


def _parse_credentials_file(path: str, profile: str = "default"):
    """Parse an INI-like BCE credentials file; return {key: value} for profile."""
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise SystemExit("无法读取凭据文件 {}: {}".format(path, exc))
    current = None
    sections = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1].strip()
            sections.setdefault(current, {})
            continue
        if current is None or "=" not in line:
            continue
        key, value = line.split("=", 1)
        sections[current][key.strip().lower()] = value.strip().strip('"').strip("'")
    return sections.get(profile, {})


def load_credentials():
    """Read AK/SK from env, else ~/.bce/credentials (baidu_access_key_id / baidu_secret_key)."""
    access_key = os.getenv("BAIDU_ACCESS_KEY_ID")
    secret_key = os.getenv("BAIDU_SECRET_ACCESS_KEY")
    token = os.getenv("BAIDU_SECURITY_TOKEN")
    if access_key and secret_key:
        return access_key, secret_key, token

    cred_path = os.getenv("BAIDU_CREDENTIALS_FILE", DEFAULT_CREDENTIALS_PATH)
    profile = os.getenv("BAIDU_PROFILE", "default")
    section = _parse_credentials_file(cred_path, profile)
    access_key = access_key or section.get("baidu_access_key_id")
    secret_key = secret_key or section.get("baidu_secret_key")
    if not token:
        token = section.get("baidu_security_token") or section.get("session_token")
    if not access_key or not secret_key:
        raise SystemExit(
            "缺少凭据：请在凭据文件（macOS/Linux: ~/.bce/credentials；"
            "Windows: %USERPROFILE%\\.bce\\credentials）的 [{}] 段配置 "
            "baidu_access_key_id / baidu_secret_key（勿在命令行或对话中传递密钥）"
            .format(profile))
    return access_key, secret_key, token


def _mask(value: Optional[str]) -> str:
    """Return a non-reversible hint of a key for status output (never the full value)."""
    if not value:
        return ""
    if len(value) <= 6:
        return value[0] + "***"
    return value[:3] + "***" + value[-2:]


def credentials_status() -> dict:
    """Report whether AK/SK are resolvable, without exposing secret values.

    Deterministic replacement for eyeballing the file: env vars take priority,
    then the credentials file's [profile] section. Returns a plain dict so the
    caller (or an agent) gets a factual configured/not answer.
    """
    env_ak = os.getenv("BAIDU_ACCESS_KEY_ID")
    env_sk = os.getenv("BAIDU_SECRET_ACCESS_KEY")
    cred_path = os.getenv("BAIDU_CREDENTIALS_FILE", DEFAULT_CREDENTIALS_PATH)
    profile = os.getenv("BAIDU_PROFILE", "default")
    access_key, secret_key, source = env_ak, env_sk, None
    if access_key and secret_key:
        source = "env"
    else:
        section = _parse_credentials_file(cred_path, profile)
        access_key = access_key or section.get("baidu_access_key_id")
        secret_key = secret_key or section.get("baidu_secret_key")
        if access_key and secret_key:
            source = "file"
    status = {
        "configured": bool(access_key and secret_key),
        "credentialsFile": cred_path,
        "fileExists": os.path.exists(cred_path),
        "profile": profile,
    }
    if status["configured"]:
        status["source"] = source
        status["accessKeyId"] = _mask(access_key)
    else:
        status["hint"] = (
            "未在当前执行环境找到有效 AK/SK（本检查只反映脚本所在环境/沙箱的文件系统视图）。"
            "若宿主机其实已配置 {}，很可能是沙箱未挂载该目录——应把宿主机的凭据目录挂载进沙箱后重跑本命令，"
            "而不是让用户重复创建文件；否则请按说明创建/补全该文件 [{}] 段的 "
            "baidu_access_key_id / baidu_secret_key。".format(cred_path, profile)
        )
    return status


def resolve_endpoint(config: ServiceConfig, region: Optional[str]) -> str:
    """Return the endpoint host for a region, honoring env override."""
    if region and not re.match(r"^[a-z0-9-]+$", region, re.IGNORECASE):
        raise SystemExit("--region 只能包含字母、数字和连字符：{}".format(region))
    if config.regional and region:
        return config.host_template.format(region=region)
    return os.getenv(config.endpoint_env, config.default_endpoint)


def resolve_protocol(config: ServiceConfig) -> str:
    """Return the request protocol (per-service default; env can override)."""
    protocol = os.getenv(config.protocol_env, config.default_protocol).lower()
    if protocol not in {"http", "https"}:
        raise SystemExit("{} 只能是 http 或 https".format(config.protocol_env))
    return protocol


class _IpOverrideAdapter(requests.adapters.HTTPAdapter):
    """把到 host 的连接改连 ip，同时保留 Host 头与 TLS SNI/证书校验 = host。"""

    def __init__(self, host, ip, **kw):
        """记录目标域名与要改连的内网 IP。"""
        self._host = host
        self._ip = ip
        super().__init__(**kw)

    def resolved_url(self, url):
        """把 URL 的 netloc 换成内网 IP（保留 scheme/port/path/query）。"""
        parts = urlsplit(url)
        netloc = self._ip + (":{}".format(parts.port) if parts.port else "")
        return parts._replace(netloc=netloc).geturl()

    def init_poolmanager(self, *a, **kw):
        """创建连接池时把 TLS SNI 与证书校验的 hostname 固定为原域名。"""
        kw["server_hostname"] = self._host  # SNI 用原域名
        kw["assert_hostname"] = self._host  # 证书校验按原域名
        return super().init_poolmanager(*a, **kw)

    def send(self, request, **kwargs):
        """发送前把 Host 头固定为原域名、连接目标改为内网 IP。"""
        request.headers["Host"] = self._host
        request.url = self.resolved_url(request.url)
        return super().send(request, **kwargs)


def _parse_response(response):
    """解析响应体为 JSON；非 JSON 时回退为纯文本。"""
    try:
        return response.json()
    except ValueError:
        return response.text


def _send(method, url, *, params, data, headers, auth, timeout, connect_ip=None):
    """发送一次请求；connect_ip 为空走普通 requests，否则连该 IP 但保留 Host/SNI。"""
    if not connect_ip:
        return requests.request(method, url, params=params, data=data,
                                headers=headers, auth=auth, timeout=timeout)
    host = urlsplit(url).netloc
    session = requests.Session()
    adapter = _IpOverrideAdapter(host, connect_ip)
    session.mount("https://{}".format(host), adapter)
    session.mount("http://{}".format(host), adapter)
    try:
        return session.request(method, url, params=params, data=data,
                               headers=headers, auth=auth, timeout=timeout)
    finally:
        session.close()


def run_request(config, method, path, *, query=None, body=None, region=None,
                allow_write=False, timeout=30, show_headers=False):
    """Sign and send one OpenAPI request; return {status, body[, headers]}."""
    method = method.upper()
    if not path.startswith("/"):
        raise SystemExit("--path 必须以 / 开头，例如 /v1/instance")
    if method not in READ_METHODS and not allow_write:
        raise SystemExit(
            "{} 是写操作，需显式加 --allow-write（并先与用户确认）".format(method))
    access_key, secret_key, token = load_credentials()
    url = "{}://{}{}".format(
        resolve_protocol(config), resolve_endpoint(config, region), path)
    headers = {}
    data = None
    if body is not None:
        data = body if isinstance(body, str) else json.dumps(body)
        headers["Content-Type"] = "application/json"
    auth = BceIamAuth(access_key, secret_key, security_token=token)
    params = list(query or [])
    response = _send(method, url, params=params, data=data,
                     headers=headers, auth=auth, timeout=timeout)
    parsed = _parse_response(response)
    status = response.status_code
    hint = None
    if detect_ip_not_allowed(status, parsed):
        host = urlsplit(url).netloc
        ip = load_internal_hosts().get(host)
        if ip:
            response = _send(method, url, params=params, data=data,
                             headers=headers, auth=auth, timeout=timeout, connect_ip=ip)
            parsed = _parse_response(response)
            status = response.status_code
            if detect_ip_not_allowed(status, parsed):
                hint = ("已按 internal_hosts.json 将 {} 定向到 {} 重试，仍报 request ip not allowed；"
                        "请确认该内网 IP 是否最新（可重跑 scripts/resolve-internal-hosts.sh）。"
                        .format(host, ip))
        else:
            hint = ("{} 命中 request ip not allowed 但 internal_hosts.json 无该域名映射；"
                    "请在开发机运行 bash scripts/resolve-internal-hosts.sh 补全后重试。"
                    .format(host))
    result = {"status": status, "body": redact(parsed)}
    if hint:
        result["internalHostsHint"] = hint
    if show_headers:
        result["headers"] = redact(dict(response.headers))
    return result


def parse_query(pairs):
    """Parse repeated ``k=v`` CLI values into ordered (key, value) tuples."""
    parsed = []
    for item in pairs or []:
        if "=" not in item:
            raise SystemExit("--query 需为 k=v 形式：{}".format(item))
        key, value = item.split("=", 1)
        parsed.append((key, value))
    return parsed


def _ensure_utf8_output() -> None:
    """Make stdout/stderr tolerate non-ASCII on any OS.

    Windows consoles default to a local code page (cp1252/cp936/...) that raises
    UnicodeEncodeError when we print Chinese API responses or the 请求失败 message;
    macOS/Linux default to UTF-8. Reconfigure both streams to UTF-8 so the CLI
    behaves the same everywhere. No-op if the stream can't be reconfigured.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="backslashreplace")
        except (ValueError, OSError):
            pass


_NETWORK_HINT = (
    "疑似当前执行环境（沙箱）未放行出网，导致无法解析或连接 OpenAPI 域名——"
    "这不是凭据或签名问题。请在你的 agent/沙箱中允许对百度云 OpenAPI 域名 "
    "*.baidubce.com（如涉及日志/备份下载再加 *.bcebos.com）的网络访问，"
    "或以带网络的方式重跑；确认放行后重试同一条命令即可。"
)


# Top-level body `code` values that signal success rather than a business error.
_SUCCESS_CODES = {"ok", "success"}


def detect_business_error(body: object) -> Optional[str]:
    """Return the business error code if a 2xx body still signals API failure.

    Some BCE interfaces (notably BCM 数据查询类) answer parameter errors or
    "no data" with HTTP 200 and an error code in the body, e.g.
    ``{"code": "INVALID_PARAMETER", ...}``. Judging success by HTTP status alone
    would hand such failures back as exit code 0. Only a top-level string ``code``
    that is neither OK/success nor numeric-zero counts as an error; bodies with no
    top-level ``code`` (most list/detail reads) are left untouched.
    """
    if not isinstance(body, dict) or "code" not in body:
        return None
    code = body.get("code")
    if code is None:
        return None
    text = str(code).strip()
    if not text or text.lower() in _SUCCESS_CODES or text in {"0", "200"}:
        return None
    return text


_IP_NOT_ALLOWED_MARK = "request ip not allowed"


def _internal_hosts_path():
    """返回与本模块同目录的 internal_hosts.json 路径。"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "internal_hosts.json")


def load_internal_hosts():
    """读 internal_hosts.json 的 hosts 映射；缺失/损坏返回 {}。"""
    try:
        with open(_internal_hosts_path(), encoding="utf-8") as handle:
            return (json.load(handle) or {}).get("hosts", {}) or {}
    except (OSError, ValueError):
        return {}


def detect_ip_not_allowed(status, body):
    """判断响应是否为 BCE 的 request-ip-not-allowed（大小写不敏感，兼容 2xx 体内报错）。"""
    if isinstance(body, str):
        text = body
    elif isinstance(body, (dict, list)):
        text = json.dumps(body, ensure_ascii=False)
    else:
        text = str(body)
    return _IP_NOT_ALLOWED_MARK in text.lower()


def _is_network_block(exc: Exception) -> bool:
    """Heuristically detect DNS/connection failures typical of blocked egress."""
    if isinstance(exc, requests.exceptions.ConnectionError):
        return True
    text = str(exc).lower()
    needles = (
        "failed to resolve", "name or service not known", "getaddrinfo",
        "temporary failure in name resolution", "nodename nor servname",
        "max retries exceeded", "connection refused",
        "network is unreachable", "no route to host",
    )
    return any(n in text for n in needles)


def main(config: ServiceConfig, argv=None) -> int:
    """CLI entry: build, sign, send one OpenAPI request; print JSON result."""
    _ensure_utf8_output()
    ap = argparse.ArgumentParser(
        description="百度云 {} OpenAPI（IAM 签名）请求工具；写操作需 --allow-write".format(
            config.label))
    ap.add_argument("--method", default="GET", help="HTTP 方法，默认 GET")
    ap.add_argument("--path", help="以 / 开头，如 /v1/instance")
    ap.add_argument("--query", action="append", help="k=v，可重复")
    ap.add_argument("--body", help="请求体 JSON 字符串（写操作）")
    ap.add_argument("--body-file", help="从文件读取请求体")
    ap.add_argument(
        "--check-credentials",
        action="store_true",
        help="只检查本机凭据是否已配置（脱敏输出，不发起请求）",
    )
    if config.regional:
        region_help = "地域代号，如 bj/su/gz；默认 {} 或 bj".format(config.endpoint_env)
    else:
        region_help = "地域代号，如 bj/su/gz；{} 全局端点；可用 {} 覆盖".format(
            config.label, config.endpoint_env)
    ap.add_argument("--region", help=region_help)
    ap.add_argument("--allow-write", action="store_true", help="放行非 GET/HEAD 的写操作")
    ap.add_argument("--timeout", type=int, default=30, help="超时秒数，默认 30")
    ap.add_argument("--show-headers", action="store_true", help="附带脱敏后的响应头")
    args = ap.parse_args(argv)

    if args.check_credentials:
        status = credentials_status()
        print(json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if status["configured"] else 2

    if not args.path:
        ap.error("--path 为必填（除非使用 --check-credentials）")

    body = args.body
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as handle:
            body = handle.read()
    try:
        result = run_request(
            config, args.method, args.path, query=parse_query(args.query), body=body,
            region=args.region, allow_write=args.allow_write,
            timeout=args.timeout, show_headers=args.show_headers)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — never print secrets in the message
        print("{} 请求失败: {}".format(config.label, exc), file=sys.stderr)
        if _is_network_block(exc):
            print("提示：{}".format(_NETWORK_HINT), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result.get("internalHostsHint"):
        print("提示：{}".format(result["internalHostsHint"]), file=sys.stderr)
    status_ok = 200 <= result["status"] < 300
    business_error = detect_business_error(result["body"]) if status_ok else None
    if business_error is not None:
        print(
            "{} 返回 HTTP 2xx 但业务码为 {}，按失败处理".format(config.label, business_error),
            file=sys.stderr)
    return 0 if status_ok and business_error is None else 1


