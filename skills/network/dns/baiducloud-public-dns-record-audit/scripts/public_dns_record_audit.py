#!/usr/bin/env python3
"""Read-only Baidu AI Cloud public DNS record quality audit.

The network client rejects every HTTP method except GET before network I/O.
Credentials are accepted only through environment variables or an explicitly
selected owner-only JSON file outside the Skill directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import ipaddress
import json
import os
import re
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
ENDPOINT = "https://dns.baidubce.com"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
KNOWN_ZONE_STATUSES = {"running", "unregister", "nsunchange", "failed", "torenew"}
KNOWN_RECORD_STATUSES = {"running", "stopped", "failed"}
KNOWN_RECORD_TYPES = {"A", "CNAME", "MX", "TXT", "NS", "AAAA", "SRV"}
KNOWN_PRODUCT_VERSIONS = {"free", "discount", "flagship"}
MINIMUM_TTL = {"free": 300, "discount": 120, "flagship": 1}
BEIJING_TZ = dt.timezone(dt.timedelta(hours=8))


class ApiFailure(RuntimeError):
    """Sanitized API failure that never carries request authorization data."""

    def __init__(
        self,
        status: int | None,
        message: str,
        *,
        code: str | None = None,
        request_id: str | None = None,
        path: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.code = code
        self.request_id = request_id
        self.path = path

    def to_dict(self, operation: str, scope: str | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {
            "operation": operation,
            "status": self.status,
            "code": self.code,
            "message": self.message,
            "requestId": self.request_id,
            "path": self.path,
        }
        if scope:
            result["scope"] = scope
        return {key: value for key, value in result.items() if value is not None}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _quote(value: Any, *, keep_slash: bool = False) -> str:
    from urllib.parse import quote

    safe = "/.~-_" if keep_slash else ".~-_"
    return quote("" if value is None else str(value), safe=safe)


def canonical_query(params: dict[str, Any] | None) -> str:
    if not params:
        return ""
    pairs: list[str] = []
    for key, value in params.items():
        if isinstance(value, bool):
            value = str(value).lower()
        pairs.append(f"{_quote(key)}={_quote(value)}")
    return "&".join(sorted(pairs))


def bce_headers(
    access_key: str,
    secret_key: str,
    host: str,
    path: str,
    params: dict[str, Any] | None,
    *,
    timestamp: str,
    session_token: str | None = None,
    expiration_seconds: int = 1800,
) -> dict[str, str]:
    canonical_uri = _quote(path, keep_slash=True)
    auth_prefix = f"bce-auth-v1/{access_key}/{timestamp}/{expiration_seconds}"
    signing_key = hmac.new(
        secret_key.encode("utf-8"), auth_prefix.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    signed = {"host": host, "x-bce-date": timestamp}
    if session_token:
        signed["x-bce-security-token"] = session_token
    signed_names = sorted(signed)
    canonical_headers = "\n".join(
        f"{_quote(name.lower())}:{_quote(str(signed[name]).strip())}" for name in signed_names
    )
    string_to_sign = "\n".join(("GET", canonical_uri, canonical_query(params), canonical_headers))
    signature = hmac.new(
        signing_key.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    headers = {
        "Host": host,
        "x-bce-date": timestamp,
        "Authorization": f"{auth_prefix}/{';'.join(signed_names)}/{signature}",
        "Accept": "application/json",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "baiducloud-public-dns-record-audit/1.0",
    }
    if session_token:
        headers["x-bce-security-token"] = session_token
    return headers


class ReadOnlyBceClient:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        session_token: str | None = None,
        *,
        timeout: float = 20.0,
        max_retries: int = 3,
    ) -> None:
        self.endpoint = ENDPOINT
        self.host = "dns.baidubce.com"
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.timeout = timeout
        self.max_retries = max_retries

    def _redact(self, text: str) -> str:
        result = text[:500]
        for value in (self.access_key, self.secret_key, self.session_token):
            if value:
                result = result.replace(value, "[REDACTED]")
        return result

    def request_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        method: str = "GET",
    ) -> dict[str, Any]:
        if method.upper() != "GET":
            raise ValueError("Read-only guard rejected non-GET request")
        if not path.startswith("/"):
            raise ValueError("API path must start with /")

        query = canonical_query(params)
        url = f"{self.endpoint}{path}"
        if query:
            url = f"{url}?{query}"

        for attempt in range(self.max_retries + 1):
            timestamp = utc_now()
            headers = bce_headers(
                self.access_key,
                self.secret_key,
                self.host,
                path,
                params,
                timestamp=timestamp,
                session_token=self.session_token,
            )
            request = urllib.request.Request(url, headers=headers, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    payload = response.read()
                    if not payload:
                        return {}
                    parsed = json.loads(payload.decode("utf-8"))
                    if not isinstance(parsed, dict):
                        raise ApiFailure(
                            response.status,
                            "Expected a JSON object response",
                            request_id=response.headers.get("x-bce-request-id"),
                            path=path,
                        )
                    return parsed
            except urllib.error.HTTPError as exc:
                detail = _parse_error_body(exc.read().decode("utf-8", errors="replace"))
                if exc.code in RETRYABLE_STATUS and attempt < self.max_retries:
                    time.sleep(min(2**attempt, 8))
                    continue
                raise ApiFailure(
                    exc.code,
                    self._redact(str(detail.get("message") or f"HTTP {exc.code}")),
                    code=_optional_string(detail.get("code")),
                    request_id=exc.headers.get("x-bce-request-id")
                    or _optional_string(detail.get("requestId")),
                    path=path,
                ) from None
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < self.max_retries:
                    time.sleep(min(2**attempt, 8))
                    continue
                reason = getattr(exc, "reason", None)
                raise ApiFailure(
                    None, self._redact(f"Network error: {reason or exc}"), path=path
                ) from None
            except json.JSONDecodeError as exc:
                raise ApiFailure(None, f"Invalid JSON response: {exc}", path=path) from None
        raise ApiFailure(None, "Request failed after retries", path=path)

    def paginate(
        self,
        path: str,
        item_fields: Iterable[str],
        params: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        query = dict(params or {})
        query.setdefault("maxKeys", 1000)
        marker: str | None = None
        seen_markers: set[str] = set()
        items: list[dict[str, Any]] = []
        queries = 0
        while True:
            if marker:
                query["marker"] = marker
            response = self.request_json(path, query)
            queries += 1
            page = _first_list(response, item_fields)
            items.extend(item for item in page if isinstance(item, dict))
            if not bool(response.get("isTruncated")):
                break
            next_marker = response.get("nextMarker")
            if not next_marker or str(next_marker) in seen_markers:
                raise ApiFailure(
                    None,
                    "Pagination stopped because nextMarker was missing or repeated",
                    code="PaginationLoop",
                    path=path,
                )
            marker = str(next_marker)
            seen_markers.add(marker)
        return items, queries


def _parse_error_body(body: str) -> dict[str, Any]:
    try:
        value = json.loads(body)
        return value if isinstance(value, dict) else {"message": body[:500]}
    except json.JSONDecodeError:
        return {"message": body[:500]}


def _first_list(data: dict[str, Any], fields: Iterable[str]) -> list[Any]:
    for field in fields:
        value = data.get(field)
        if isinstance(value, list):
            return value
    return []


def _optional_string(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _read_credentials_file(path: Path) -> tuple[str, str, str | None]:
    skill_root = Path(__file__).resolve().parents[1]
    if _is_within(path, skill_root):
        raise ValueError("Credentials file must be outside the Skill directory")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Credentials file must be a regular file")
        if metadata.st_uid != os.geteuid():
            raise ValueError("Credentials file must be owned by the current user")
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ValueError("Credentials file permissions are too broad; run chmod 600")
        if metadata.st_size > 65536:
            raise ValueError("Credentials file is unexpectedly large")
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            descriptor = -1
            payload = json.load(handle)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if not isinstance(payload, dict):
        raise ValueError("Credentials file must contain a JSON object")
    access_key = str(payload.get("accessKeyId") or "").strip()
    secret_key = str(payload.get("secretAccessKey") or "").strip()
    session_token = str(payload.get("sessionToken") or "").strip() or None
    if not access_key or not secret_key:
        raise ValueError("Credentials file requires accessKeyId and secretAccessKey")
    return access_key, secret_key, session_token


def _parse_requested_zones(value: str | None) -> list[str]:
    if not value:
        return []
    result: list[str] = []
    for item in value.split(","):
        zone = item.strip().rstrip(".").lower()
        if not zone:
            continue
        if not _valid_hostname(zone):
            raise ValueError(f"Invalid zone name: {item.strip()}")
        if zone not in result:
            result.append(zone)
    return result


def _zone_ascii(name: str) -> str:
    return name.rstrip(".").encode("idna").decode("ascii").lower()


def collect_live(args: argparse.Namespace) -> dict[str, Any]:
    if args.credentials_file:
        access_key, secret_key, session_token = _read_credentials_file(args.credentials_file)
    else:
        access_key = os.environ.get("BCE_ACCESS_KEY_ID")
        secret_key = os.environ.get("BCE_SECRET_ACCESS_KEY")
        session_token = os.environ.get("BCE_SESSION_TOKEN")
    if not access_key or not secret_key:
        raise ValueError(
            "Set BCE_ACCESS_KEY_ID and BCE_SECRET_ACCESS_KEY in the environment; "
            "or use --credentials-file with an owner-only JSON file; "
            "do not pass credentials on the command line"
        )

    requested = _parse_requested_zones(args.zones)
    inventory: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": utc_now(),
        "mode": "live",
        "endpoint": ENDPOINT,
        "selection": {"requestedZones": requested, "unmatchedZones": []},
        "coverage": {
            "listZones": {"status": "notAttempted", "count": 0, "queries": 0, "failedQueries": 0},
            "listRecords": {
                "status": "notAttempted",
                "successfulZones": 0,
                "failedZones": 0,
                "queries": 0,
                "recordCount": 0,
            },
        },
        "zones": [],
        "errors": [],
    }
    client = ReadOnlyBceClient(
        access_key,
        secret_key,
        session_token,
        timeout=args.timeout,
        max_retries=args.max_retries,
    )
    try:
        zones, queries = client.paginate("/v1/dns/zone", ("zones",))
    except ApiFailure as exc:
        inventory["coverage"]["listZones"].update(status="failed", failedQueries=1)
        inventory["coverage"]["listRecords"].update(
            status="blocked", reason="Zone list query failed"
        )
        inventory["errors"].append(exc.to_dict("listZones"))
        return inventory

    zone_coverage = inventory["coverage"]["listZones"]
    zone_coverage.update(status="success", count=len(zones), queries=queries)
    by_name = {
        str(zone.get("name") or "").rstrip(".").lower(): zone
        for zone in zones
        if isinstance(zone, dict) and zone.get("name")
    }
    selected = zones if not requested else [by_name[name] for name in requested if name in by_name]
    inventory["selection"]["unmatchedZones"] = [name for name in requested if name not in by_name]
    record_coverage = inventory["coverage"]["listRecords"]

    for summary in selected:
        item = dict(summary)
        item["records"] = []
        name = str(item.get("name") or "").strip()
        if not name:
            item["_recordsStatus"] = "failed"
            record_coverage["failedZones"] += 1
            inventory["errors"].append(
                {
                    "operation": "listRecords",
                    "code": "MissingZoneName",
                    "message": "Zone list item did not contain a name",
                }
            )
            inventory["zones"].append(item)
            continue
        try:
            ascii_name = _zone_ascii(name)
            path = f"/v1/dns/zone/{_quote(ascii_name)}/record"
            records, record_queries = client.paginate(path, ("records",))
            item["records"] = records
            item["_recordsStatus"] = "success"
            record_coverage["successfulZones"] += 1
            record_coverage["queries"] += record_queries
            record_coverage["recordCount"] += len(records)
        except (ApiFailure, UnicodeError) as exc:
            item["_recordsStatus"] = "failed"
            record_coverage["failedZones"] += 1
            if isinstance(exc, ApiFailure):
                inventory["errors"].append(exc.to_dict("listRecords", name))
            else:
                inventory["errors"].append(
                    {
                        "operation": "listRecords",
                        "scope": name,
                        "code": "InvalidZoneName",
                        "message": "Zone name could not be encoded with IDNA",
                    }
                )
        inventory["zones"].append(item)

    if record_coverage["failedZones"]:
        record_coverage["status"] = "partial" if record_coverage["successfulZones"] else "failed"
    else:
        record_coverage["status"] = "success"
    return inventory


def load_inventory(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        inventory = json.load(handle)
    if not isinstance(inventory, dict) or not isinstance(inventory.get("zones"), list):
        raise ValueError("Inventory must be a JSON object containing a zones list")
    inventory.setdefault("schemaVersion", SCHEMA_VERSION)
    inventory.setdefault("generatedAt", utc_now())
    inventory["mode"] = "offline"
    inventory.setdefault("endpoint", "offline")
    inventory.setdefault("selection", {"requestedZones": [], "unmatchedZones": []})
    inventory.setdefault("errors", [])
    total_records = 0
    successful = 0
    failed = 0
    for index, zone in enumerate(inventory["zones"]):
        if not isinstance(zone, dict):
            raise ValueError(f"Zone at index {index} must be an object")
        records = zone.setdefault("records", [])
        if not isinstance(records, list):
            raise ValueError(f"Zone {zone.get('name', index)} records must be a list")
        status = zone.setdefault("_recordsStatus", "unknown")
        if status == "success":
            successful += 1
            total_records += len(records)
        elif status == "failed":
            failed += 1
    coverage = inventory.setdefault("coverage", {})
    coverage.setdefault(
        "listZones",
        {"status": "unknown", "count": len(inventory["zones"]), "queries": 0, "failedQueries": 0},
    )
    coverage.setdefault(
        "listRecords",
        {
            "status": "unknown",
            "successfulZones": successful,
            "failedZones": failed,
            "queries": 0,
            "recordCount": total_records,
        },
    )
    return inventory


def _finding(
    rule_id: str,
    severity: str,
    zone: dict[str, Any] | None,
    record: dict[str, Any] | None,
    fact: str,
    interpretation: str,
    *,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    zone = zone or {}
    record = record or {}
    return {
        "ruleId": rule_id,
        "severity": severity,
        "zoneName": _optional_string(zone.get("name")),
        "zoneId": _optional_string(zone.get("id")),
        "recordId": _optional_string(record.get("id")),
        "rr": _optional_string(record.get("rr")),
        "type": _optional_string(record.get("type")),
        "line": _optional_string(record.get("line")),
        "fact": fact,
        "interpretation": interpretation,
        "evidence": evidence or {},
    }


def _parse_timestamp(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    parsed: dt.datetime | None = None
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = dt.datetime.strptime(text, pattern)
                break
            except ValueError:
                continue
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=BEIJING_TZ)
    return parsed.astimezone(dt.timezone.utc)


def _valid_hostname(value: str) -> bool:
    text = value.strip().rstrip(".")
    if not text or len(text) > 253 or ".." in text:
        return False
    try:
        ascii_text = text.encode("idna").decode("ascii")
    except UnicodeError:
        return False
    for label in ascii_text.split("."):
        if not label or len(label) > 63:
            return False
        if label.startswith("-") or label.endswith("-"):
            return False
        if not re.fullmatch(r"[A-Za-z0-9-]+", label):
            return False
    return True


def _valid_wildcard_rr(rr: str) -> tuple[bool, bool]:
    if "*" not in rr:
        return False, True
    parts = rr.split(".")
    return True, parts[0] == "*" and all("*" not in part for part in parts[1:])


def _record_key(record: dict[str, Any]) -> tuple[str, str, str, str, str]:
    priority = "" if record.get("priority") is None else str(record.get("priority"))
    return (
        str(record.get("rr") or "").rstrip(".").lower(),
        str(record.get("type") or "").upper(),
        str(record.get("value") or "").strip().rstrip(".").lower(),
        str(record.get("line") or "default").lower(),
        priority,
    )


def analyze_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    zone_statuses: Counter[str] = Counter()
    record_statuses: Counter[str] = Counter()
    record_types: Counter[str] = Counter()
    lines: Counter[str] = Counter()
    versions: Counter[str] = Counter()
    total_records = 0
    now = dt.datetime.now(dt.timezone.utc)

    zones_by_name = {
        str(zone.get("name") or "").lower(): zone
        for zone in inventory.get("zones", [])
        if isinstance(zone, dict)
    }
    for error in inventory.get("errors", []):
        if not isinstance(error, dict):
            continue
        status_code = error.get("status")
        rule_id = "COV-002" if status_code in (401, 403) else "COV-004" if status_code == 404 else "COV-001"
        severity = "info" if rule_id == "COV-004" else "high"
        zone = zones_by_name.get(str(error.get("scope") or "").lower())
        findings.append(
            _finding(
                rule_id,
                severity,
                zone,
                None,
                f"{error.get('operation', 'query')} 查询失败，状态为 {status_code or 'network-error'}",
                "该范围的域名或解析记录覆盖不完整",
                evidence={
                    key: error.get(key)
                    for key in ("operation", "status", "code", "requestId", "path", "scope")
                    if error.get(key) is not None
                },
            )
        )

    unmatched = inventory.get("selection", {}).get("unmatchedZones", [])
    for zone_name in unmatched if isinstance(unmatched, list) else []:
        findings.append(
            _finding(
                "COV-001",
                "high",
                {"name": zone_name},
                None,
                "指定域名未在成功返回的域名列表中精确匹配",
                "可能是域名不存在、当前身份不可见或名称输入有误，不能视为已审计",
                evidence={"requestedZone": zone_name},
            )
        )

    for zone in inventory.get("zones", []):
        if not isinstance(zone, dict):
            continue
        zone_name = str(zone.get("name") or "")
        zone_status = str(zone.get("status") or "").lower()
        version = str(zone.get("productVersion") or "").lower()
        zone_statuses[zone_status or "missing"] += 1
        versions[version or "missing"] += 1

        if zone_status == "failed":
            findings.append(_finding("ZONE-001", "high", zone, None, "域名状态为 failed", "服务控制面报告域名异常", evidence={"status": zone_status}))
        elif zone_status in {"unregister", "nsunchange", "torenew"}:
            findings.append(_finding("ZONE-001", "medium", zone, None, f"域名状态为 {zone_status}", "注册、NS 或备案/续期状态需要人工处理", evidence={"status": zone_status}))
        elif zone_status not in KNOWN_ZONE_STATUSES:
            findings.append(_finding("DNS-014", "info", zone, None, f"域名状态为 {zone_status or 'missing'}", "状态缺失或不在当前官方枚举中", evidence={"status": zone_status or None}))

        if version not in KNOWN_PRODUCT_VERSIONS:
            findings.append(_finding("DNS-014", "info", zone, None, f"产品版本为 {version or 'missing'}", "无法应用版本最小 TTL 阈值", evidence={"productVersion": version or None}))

        expiration = _parse_timestamp(zone.get("expireTime"))
        if expiration is not None:
            days = (expiration - now).total_seconds() / 86400
            if days <= 30:
                severity = "high" if days < 0 else "medium"
                findings.append(
                    _finding(
                        "ZONE-002",
                        severity,
                        zone,
                        None,
                        f"域名解析服务距离到期约 {int(days)} 天",
                        "需要人工确认续期或替代安排；本 Skill 不执行续费",
                        evidence={"expireTime": zone.get("expireTime"), "daysRemaining": round(days, 2)},
                    )
                )

        records = zone.get("records", [])
        if not isinstance(records, list):
            continue
        if zone.get("_recordsStatus") == "success" and not records:
            findings.append(_finding("ZONE-003", "info", zone, None, "记录查询成功且返回零条记录", "该域名当前配置快照为空", evidence={"recordCount": 0}))
        if zone.get("_recordsStatus") != "success":
            continue
        total_records += len(records)

        active_groups: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        exact_groups: defaultdict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
        owners: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

        for record in records:
            if not isinstance(record, dict):
                continue
            status = str(record.get("status") or "").lower()
            record_type = str(record.get("type") or "").upper()
            line = str(record.get("line") or "default").lower()
            rr = str(record.get("rr") or "").strip().rstrip(".").lower()
            value = str(record.get("value") or "").strip()
            record_statuses[status or "missing"] += 1
            record_types[record_type or "missing"] += 1
            lines[line or "missing"] += 1

            if status == "failed":
                findings.append(_finding("DNS-009", "high", zone, record, "解析记录状态为 failed", "服务控制面报告记录异常", evidence={"status": status}))
            elif status == "stopped":
                findings.append(_finding("DNS-009", "low", zone, record, "解析记录状态为 stopped", "记录已暂停，可能是计划内配置，需要确认意图", evidence={"status": status}))
            elif status not in KNOWN_RECORD_STATUSES:
                findings.append(_finding("DNS-014", "info", zone, record, f"解析记录状态为 {status or 'missing'}", "状态缺失或不在当前官方枚举中", evidence={"status": status or None}))

            if record_type not in KNOWN_RECORD_TYPES:
                findings.append(_finding("DNS-014", "info", zone, record, f"记录类型为 {record_type or 'missing'}", "类型缺失或不在当前 API 模型枚举中，不做格式推断", evidence={"type": record_type or None}))

            ttl = record.get("ttl")
            minimum = MINIMUM_TTL.get(version)
            if not isinstance(ttl, int) or isinstance(ttl, bool) or ttl <= 0:
                findings.append(_finding("DNS-007", "high", zone, record, f"TTL 为 {ttl!r}", "TTL 必须是正整数", evidence={"ttl": ttl, "productVersion": version or None}))
            elif minimum is not None and ttl < minimum:
                findings.append(_finding("DNS-007", "high", zone, record, f"TTL={ttl} 低于 {version} 版本最小值 {minimum}", "配置与当前产品版本约束不一致", evidence={"ttl": ttl, "minimumTtl": minimum, "productVersion": version}))

            if record_type == "A":
                try:
                    address = ipaddress.IPv4Address(value)
                    if not address.is_global:
                        findings.append(_finding("DNS-013", "info", zone, record, "公网 A 记录指向非全局 IPv4 地址", "可能是有意配置；需结合业务设计确认", evidence={"value": value}))
                except ipaddress.AddressValueError:
                    findings.append(_finding("DNS-001", "high", zone, record, "A 记录值不是合法的单个 IPv4 地址", "记录值与 A 类型格式不符", evidence={"value": value}))
            elif record_type == "AAAA":
                try:
                    address6 = ipaddress.IPv6Address(value)
                    if not address6.is_global:
                        findings.append(_finding("DNS-013", "info", zone, record, "公网 AAAA 记录指向非全局 IPv6 地址", "可能是有意配置；需结合业务设计确认", evidence={"value": value}))
                except ipaddress.AddressValueError:
                    findings.append(_finding("DNS-002", "high", zone, record, "AAAA 记录值不是合法的单个 IPv6 地址", "记录值与 AAAA 类型格式不符", evidence={"value": value}))
            elif record_type in {"CNAME", "NS", "MX"} and not _valid_hostname(value):
                findings.append(_finding("DNS-003", "high", zone, record, f"{record_type} 目标不是合法 DNS 主机名", "目标值需要人工修正或确认", evidence={"value": value}))
            elif record_type == "SRV":
                parts = value.split()
                valid = len(parts) == 4
                if valid:
                    try:
                        priority, weight, port = (int(parts[index]) for index in range(3))
                        valid = all(0 <= number <= 65535 for number in (priority, weight, port)) and _valid_hostname(parts[3])
                    except ValueError:
                        valid = False
                if not valid:
                    findings.append(_finding("DNS-015", "medium", zone, record, "SRV 记录值不符合 priority weight port target 格式", "记录值与官方 SRV 格式说明不一致", evidence={"value": value}))

            if record_type == "MX":
                priority = record.get("priority")
                if not isinstance(priority, int) or isinstance(priority, bool) or not 0 <= priority <= 50:
                    findings.append(_finding("DNS-008", "medium", zone, record, f"MX priority 为 {priority!r}", "MX 优先级必须为 0 至 50 的整数", evidence={"priority": priority}))

            has_wildcard, valid_wildcard = _valid_wildcard_rr(rr)
            if has_wildcard and valid_wildcard:
                findings.append(_finding("DNS-010", "low", zone, record, f"主机记录 {rr} 使用泛解析", "泛解析覆盖范围较广，需确认与显式记录的治理意图", evidence={"rr": rr}))
            elif has_wildcard:
                findings.append(_finding("DNS-011", "high", zone, record, f"主机记录 {rr} 的通配符位置无效", "通配符只能作为最左侧完整标签", evidence={"rr": rr}))

            if status == "running":
                active_groups[(rr, line)].append(record)
                exact_groups[_record_key(record)].append(record)
                owners[rr].append(record)

        for (rr, line), group in active_groups.items():
            types = {str(record.get("type") or "").upper() for record in group}
            cname_records = [record for record in group if str(record.get("type") or "").upper() == "CNAME"]
            if cname_records and len(types) > 1:
                findings.append(
                    _finding(
                        "DNS-004", "high", zone, cname_records[0],
                        f"同一主机记录和线路同时存在 CNAME 与 {', '.join(sorted(types - {'CNAME'}))}",
                        "同一 DNS 视图中的 CNAME 与其他数据冲突",
                        evidence={"rr": rr, "line": line, "types": sorted(types), "recordIds": [_optional_string(item.get('id')) for item in group]},
                    )
                )
            cname_targets = {str(record.get("value") or "").strip().rstrip(".").lower() for record in cname_records}
            if len(cname_targets) > 1:
                findings.append(_finding("DNS-005", "medium", zone, cname_records[0], "同一主机记录和线路存在多个 CNAME 目标", "一个别名应有唯一规范目标", evidence={"rr": rr, "line": line, "targets": sorted(cname_targets)}))

        for key, group in exact_groups.items():
            if len(group) > 1:
                findings.append(_finding("DNS-006", "low", zone, group[0], f"发现 {len(group)} 条完全相同的活动记录", "可能是冗余配置；不同值的多记录不会命中此规则", evidence={"rr": key[0], "type": key[1], "value": key[2], "line": key[3], "priority": key[4] or None, "recordIds": [_optional_string(item.get('id')) for item in group]}))

        for rr, group in owners.items():
            owner_lines = {str(record.get("line") or "default").lower() for record in group}
            if owner_lines and "default" not in owner_lines:
                findings.append(_finding("DNS-012", "low", zone, group[0], f"活动主机记录 {rr or '[empty]'} 只有线路特定配置", "可能缺少面向其他来源的默认线路回退；需按设计确认", evidence={"rr": rr, "lines": sorted(owner_lines), "recordIds": [_optional_string(item.get('id')) for item in group]}))

    findings.sort(
        key=lambda item: (
            SEVERITY_ORDER.get(str(item.get("severity")), 9),
            str(item.get("zoneName") or ""),
            str(item.get("ruleId") or ""),
            str(item.get("recordId") or ""),
        )
    )
    return {
        "summary": {
            "zoneCount": len([zone for zone in inventory.get("zones", []) if isinstance(zone, dict)]),
            "recordCountInSuccessfulZones": total_records,
            "findingsBySeverity": dict(Counter(item["severity"] for item in findings)),
            "zoneStatusDistribution": dict(sorted(zone_statuses.items())),
            "productVersionDistribution": dict(sorted(versions.items())),
            "recordStatusDistribution": dict(sorted(record_statuses.items())),
            "recordTypeDistribution": dict(sorted(record_types.items())),
            "lineDistribution": dict(sorted(lines.items())),
        },
        "findings": findings,
    }


def _markdown(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(inventory: dict[str, Any]) -> str:
    analysis = inventory.get("analysis", {})
    summary = analysis.get("summary", {})
    findings = analysis.get("findings", [])
    list_zones = inventory.get("coverage", {}).get("listZones", {})
    list_records = inventory.get("coverage", {}).get("listRecords", {})
    lines = [
        "# 百度智能云公网 DNS 解析记录质量审计报告",
        "",
        f"- 生成时间：{_markdown(inventory.get('generatedAt'))}",
        f"- 模式：{_markdown(inventory.get('mode'))}",
        f"- Endpoint：{_markdown(inventory.get('endpoint'))}",
        f"- 域名数：{summary.get('zoneCount', 0)}",
        f"- 成功查询域名中的记录数：{summary.get('recordCountInSuccessfulZones', 0)}",
        "",
        "## 采集覆盖率",
        "",
        "| 操作 | 状态 | 成功/数量 | 失败 | GET 请求页数 |",
        "|---|---|---:|---:|---:|",
        f"| 域名列表 | {_markdown(list_zones.get('status'))} | {list_zones.get('count', 0)} | {list_zones.get('failedQueries', 0)} | {list_zones.get('queries', 0)} |",
        f"| 每域名记录列表 | {_markdown(list_records.get('status'))} | {list_records.get('successfulZones', 0)} | {list_records.get('failedZones', 0)} | {list_records.get('queries', 0)} |",
        "",
    ]
    unmatched = inventory.get("selection", {}).get("unmatchedZones", [])
    if unmatched:
        lines.extend([f"指定但未精确匹配的域名：{', '.join(_markdown(item) for item in unmatched)}", ""])

    lines.extend(["## 域名概览", "", "| 域名 | 状态 | 产品版本 | 到期时间 | 记录查询 | 记录数 |", "|---|---|---|---|---|---:|"])
    for zone in inventory.get("zones", []):
        if not isinstance(zone, dict):
            continue
        records = zone.get("records", [])
        count = len(records) if zone.get("_recordsStatus") == "success" and isinstance(records, list) else "-"
        lines.append(f"| {_markdown(zone.get('name'))} | {_markdown(zone.get('status'))} | {_markdown(zone.get('productVersion'))} | {_markdown(zone.get('expireTime'))} | {_markdown(zone.get('_recordsStatus'))} | {count} |")

    lines.extend(["", "## 分布", ""])
    for label, key in (
        ("域名状态", "zoneStatusDistribution"),
        ("产品版本", "productVersionDistribution"),
        ("记录状态", "recordStatusDistribution"),
        ("记录类型", "recordTypeDistribution"),
        ("解析线路", "lineDistribution"),
    ):
        value = summary.get(key, {})
        lines.append(f"- {label}：`{json.dumps(value, ensure_ascii=False, sort_keys=True)}`")

    lines.extend(["", "## 发现", ""])
    if not findings:
        lines.append("在成功查询且规则覆盖的配置范围内未发现规则命中。")
    else:
        lines.extend(["| 严重度 | 规则 | 域名 | RR | 类型/线路 | 事实 |", "|---|---|---|---|---|---|"])
        for item in findings:
            type_line = f"{item.get('type') or '-'} / {item.get('line') or '-'}"
            lines.append(f"| {_markdown(item.get('severity'))} | {_markdown(item.get('ruleId'))} | {_markdown(item.get('zoneName'))} | {_markdown(item.get('rr'))} | {_markdown(type_line)} | {_markdown(item.get('fact'))} |")
        lines.extend(["", "### 证据与解释", ""])
        for item in findings:
            identity = f"{item.get('zoneName') or '-'} / {item.get('recordId') or '-'}"
            lines.extend([
                f"- **{_markdown(item.get('severity')).upper()} {item.get('ruleId')} — {_markdown(identity)}**：{_markdown(item.get('fact'))}",
                f"  - 解释：{_markdown(item.get('interpretation'))}",
                f"  - 证据：`{json.dumps(item.get('evidence', {}), ensure_ascii=False, sort_keys=True)}`",
            ])

    lines.extend([
        "",
        "## 限制",
        "",
        "- 本报告只反映百度智能云公网 DNS 控制面在采集时刻返回的配置。",
        "- 未执行公网 DNS 查询，不验证权威应答、递归缓存、DNSSEC、传播状态、目标可达性或业务可用性。",
        "- `stopped`、泛解析、非全局 IP 和缺少默认线路均可能是有意设计，需要结合变更记录与业务架构人工确认。",
        "- 查询失败的范围不计为零资源，也不能形成无风险结论。",
        "",
    ])
    return "\n".join(lines)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_outputs(inventory: dict[str, Any], output_dir: Path) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    if _is_within(output_dir, skill_root):
        raise ValueError("Output directory must be outside the Skill directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory_text = json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    _atomic_write(output_dir / "inventory.json", inventory_text)
    _atomic_write(output_dir / "report.md", render_report(inventory))


def self_test() -> None:
    assert canonical_query({"maxKeys": 1000, "marker": "a b"}) == "marker=a%20b&maxKeys=1000"
    headers = bce_headers("ak", "sk", "dns.baidubce.com", "/v1/dns/zone", {"maxKeys": 1000}, timestamp="2026-01-01T00:00:00Z")
    assert headers["Authorization"].startswith("bce-auth-v1/ak/")
    client = ReadOnlyBceClient("ak", "sk", max_retries=0)
    try:
        client.request_json("/v1/dns/zone", method="POST")
    except ValueError as exc:
        assert "non-GET" in str(exc)
    else:
        raise AssertionError("Read-only guard did not reject POST")
    assert _valid_hostname("xn--fsqu00a.xn--0zwm56d")
    assert not _valid_hostname("bad_name.example")
    assert _valid_wildcard_rr("*.api") == (True, True)
    assert _valid_wildcard_rr("api.*") == (True, False)

    sample = {
        "zones": [
            {
                "name": "example.com",
                "status": "running",
                "productVersion": "free",
                "_recordsStatus": "success",
                "records": [
                    {"id": "1", "rr": "www", "status": "running", "type": "CNAME", "value": "target.example", "ttl": 300, "line": "default"},
                    {"id": "2", "rr": "www", "status": "running", "type": "A", "value": "192.0.2.1", "ttl": 300, "line": "default"},
                    {"id": "3", "rr": "v6", "status": "running", "type": "AAAA", "value": "bad", "ttl": 100, "line": "default"},
                ],
            }
        ],
        "errors": [],
        "selection": {"unmatchedZones": []},
    }
    rule_ids = {item["ruleId"] for item in analyze_inventory(sample)["findings"]}
    assert {"DNS-002", "DNS-004", "DNS-007", "DNS-013"}.issubset(rule_ids)
    print("self-test: ok")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only Baidu AI Cloud public DNS record quality audit")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--input", type=Path, help="Offline inventory JSON")
    mode.add_argument("--self-test", action="store_true", help="Run local tests without network access")
    parser.add_argument("--credentials-file", type=Path, help="Owner-only JSON credential file outside the Skill directory")
    parser.add_argument("--zones", help="Comma-separated exact zone names; live mode only")
    parser.add_argument("--output-dir", type=Path, help="Directory outside the Skill for inventory.json and report.md")
    parser.add_argument("--timeout", type=float, default=20.0, help="Per-request timeout in seconds")
    parser.add_argument("--max-retries", type=int, default=3, choices=range(0, 6), help="Retries for the same GET request")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            self_test()
            return 0
        if not args.output_dir:
            parser.error("--output-dir is required unless --self-test is used")
        if args.input:
            if args.credentials_file or args.zones:
                parser.error("--credentials-file and --zones cannot be used with --input")
            inventory = load_inventory(args.input)
        else:
            inventory = collect_live(args)
        inventory["analysis"] = analyze_inventory(inventory)
        write_outputs(inventory, args.output_dir)
        summary = inventory["analysis"]["summary"]
        print(
            "audit complete: "
            f"zones={summary['zoneCount']} "
            f"records={summary['recordCountInSuccessfulZones']} "
            f"findings={len(inventory['analysis']['findings'])}"
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
