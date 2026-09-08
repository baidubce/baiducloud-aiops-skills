#!/usr/bin/env python3
"""Read-only Baidu AI Cloud VPC security group and ACL auditor."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import ipaddress
import json
import os
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Iterable


SCHEMA_VERSION = "1.0"
RESOURCE_KEYS = ("vpcs", "securityGroups", "enterpriseSecurityGroups", "acls")
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
SENSITIVE_PORTS = {
    22,
    23,
    1433,
    1521,
    2049,
    2375,
    2376,
    3306,
    3389,
    5432,
    5900,
    6379,
    6443,
    9200,
    11211,
    27017,
}


class ApiFailure(RuntimeError):
    """Sanitized API failure that never includes authorization material."""

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

    def to_dict(self, resource_type: str, scope: str | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {
            "resourceType": resource_type,
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
    pairs = []
    for key, value in params.items():
        if isinstance(value, bool):
            value = str(value).lower()
        pairs.append(f"{_quote(key)}={_quote(value)}")
    return "&".join(sorted(pairs))


def bce_authorization(
    access_key: str,
    secret_key: str,
    host: str,
    path: str,
    params: dict[str, Any] | None,
    *,
    timestamp: str,
    session_token: str | None = None,
    expiration_seconds: int = 1800,
) -> tuple[str, dict[str, str]]:
    method = "GET"
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
    string_to_sign = "\n".join(
        (method, canonical_uri, canonical_query(params), canonical_headers)
    )
    signature = hmac.new(
        signing_key.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    authorization = f"{auth_prefix}/{';'.join(signed_names)}/{signature}"
    headers = {
        "Host": host,
        "x-bce-date": timestamp,
        "Authorization": authorization,
        "Accept": "application/json",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "baiducloud-vpc-security-policy-audit/1.0",
    }
    if session_token:
        headers["x-bce-security-token"] = session_token
    return authorization, headers


class ReadOnlyBceClient:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        session_token: str | None = None,
        *,
        timeout: float = 20.0,
        max_retries: int = 3,
    ) -> None:
        endpoint = endpoint.rstrip("/")
        if not endpoint.startswith("https://"):
            raise ValueError("Endpoint must use HTTPS")
        from urllib.parse import urlparse

        parsed = urlparse(endpoint)
        if not parsed.hostname or parsed.path not in ("", "/"):
            raise ValueError("Endpoint must be an HTTPS origin without a path")
        if not parsed.hostname.endswith(".baidubce.com"):
            raise ValueError("Endpoint host must be an official *.baidubce.com domain")
        self.endpoint = endpoint
        self.host = parsed.netloc
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.timeout = timeout
        self.max_retries = max_retries

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
            _, headers = bce_authorization(
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
                body = exc.read().decode("utf-8", errors="replace")
                detail = _parse_error_body(body)
                if exc.code in RETRYABLE_STATUS and attempt < self.max_retries:
                    time.sleep(min(2**attempt, 8))
                    continue
                raise ApiFailure(
                    exc.code,
                    detail.get("message") or f"HTTP {exc.code}",
                    code=detail.get("code"),
                    request_id=exc.headers.get("x-bce-request-id") or detail.get("requestId"),
                    path=path,
                ) from None
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < self.max_retries:
                    time.sleep(min(2**attempt, 8))
                    continue
                reason = getattr(exc, "reason", None)
                raise ApiFailure(None, f"Network error: {reason or exc}", path=path) from None
            except json.JSONDecodeError as exc:
                raise ApiFailure(None, f"Invalid JSON response: {exc}", path=path) from None
        raise ApiFailure(None, "Request failed after retries", path=path)

    def paginate(
        self,
        path: str,
        item_fields: Iterable[str],
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        query = dict(params or {})
        query.setdefault("maxKeys", 1000)
        marker: str | None = None
        seen_markers: set[str] = set()
        items: list[dict[str, Any]] = []
        while True:
            if marker:
                query["marker"] = marker
            response = self.request_json(path, query)
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
        return items


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


def _resource_id(record: dict[str, Any], *fields: str) -> str | None:
    for field in fields:
        value = record.get(field)
        if value not in (None, ""):
            return str(value)
    return None


def _new_region(endpoint: str) -> dict[str, Any]:
    return {
        "endpoint": endpoint,
        "resources": {key: [] for key in RESOURCE_KEYS},
        "coverage": {
            key: {"status": "notAttempted", "count": 0, "queries": 0, "failedQueries": 0}
            for key in RESOURCE_KEYS
        },
        "errors": [],
    }


def _record_query(
    region_data: dict[str, Any],
    resource_type: str,
    scope: str,
    query: Callable[[], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    coverage = region_data["coverage"][resource_type]
    coverage["queries"] += 1
    try:
        records = query()
        region_data["resources"][resource_type].extend(records)
        coverage["count"] = len(region_data["resources"][resource_type])
        coverage["status"] = "success" if coverage["failedQueries"] == 0 else "partial"
        return records
    except ApiFailure as exc:
        coverage["failedQueries"] += 1
        coverage["status"] = "failed" if coverage["count"] == 0 else "partial"
        region_data["errors"].append(exc.to_dict(resource_type, scope))
        return []


def collect_region(
    region: str,
    endpoint: str,
    access_key: str,
    secret_key: str,
    session_token: str | None,
    timeout: float,
    max_retries: int,
    requested_vpcs: list[str],
) -> dict[str, Any]:
    client = ReadOnlyBceClient(
        endpoint,
        access_key,
        secret_key,
        session_token,
        timeout=timeout,
        max_retries=max_retries,
    )
    data = _new_region(endpoint)
    vpcs = _record_query(
        data,
        "vpcs",
        region,
        lambda: client.paginate("/v1/vpc", ("vpcs",)),
    )
    returned_ids = {_resource_id(item, "vpcId", "id") for item in vpcs}
    returned_ids.discard(None)
    if requested_vpcs:
        missing = [vpc_id for vpc_id in requested_vpcs if vpc_id not in returned_ids]
        if missing and data["coverage"]["vpcs"]["status"] == "success":
            raise ValueError("Requested VPC IDs were not returned: " + ", ".join(missing))
        selected_ids = [vpc_id for vpc_id in requested_vpcs if vpc_id in returned_ids]
    else:
        selected_ids = sorted(returned_ids)

    if requested_vpcs:
        for vpc_id in selected_ids:
            _record_query(
                data,
                "securityGroups",
                vpc_id,
                lambda vpc_id=vpc_id: client.paginate(
                    "/v2/securityGroup", ("securityGroups",), {"vpcId": vpc_id}
                ),
            )
    else:
        _record_query(
            data,
            "securityGroups",
            region,
            lambda: client.paginate("/v2/securityGroup", ("securityGroups",)),
        )

    _record_query(
        data,
        "enterpriseSecurityGroups",
        region,
        lambda: client.paginate(
            "/v1/enterprise/security", ("enterpriseSecurityGroups",)
        ),
    )

    for vpc_id in selected_ids:
        def acl_query(vpc_id: str = vpc_id) -> list[dict[str, Any]]:
            response = client.request_json("/v1/acl", {"vpcId": vpc_id})
            entries = _first_list(response, ("aclEntrys", "aclEntries"))
            result = []
            for entry in entries:
                if isinstance(entry, dict):
                    entry = dict(entry)
                    entry.setdefault("vpcId", response.get("vpcId") or vpc_id)
                    entry.setdefault("vpcName", response.get("vpcName"))
                    entry.setdefault("vpcCidr", response.get("vpcCidr"))
                    result.append(entry)
            return result

        _record_query(data, "acls", vpc_id, acl_query)

    if not selected_ids and data["coverage"]["vpcs"]["status"] == "success":
        data["coverage"]["acls"]["status"] = "success"
        data["coverage"]["acls"]["count"] = 0
    elif not selected_ids:
        data["coverage"]["acls"]["status"] = "blocked"
        data["coverage"]["acls"]["reason"] = "No successfully collected VPC ID was available"
    data["selectedVpcIds"] = selected_ids
    return data


def _read_credentials_file(path: Path) -> tuple[str, str, str | None]:
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


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    result = []
    for item in value.split(","):
        item = item.strip()
        if item and item not in result:
            result.append(item)
    return result


def _parse_regions(value: str | None) -> list[str]:
    regions = _parse_csv(value)
    if not regions:
        raise ValueError("--regions is required in live mode")
    for region in regions:
        if not all(ch.isalnum() or ch == "-" for ch in region):
            raise ValueError(f"Invalid region code: {region}")
    return [item.lower() for item in regions]


def _parse_endpoints(values: list[str]) -> dict[str, str]:
    result = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--endpoint must use REGION=https://host form")
        region, endpoint = value.split("=", 1)
        result[region.strip().lower()] = endpoint.strip()
    return result


def collect_live(args: argparse.Namespace) -> dict[str, Any]:
    if args.credentials_file:
        access_key, secret_key, session_token = _read_credentials_file(args.credentials_file)
    else:
        access_key = os.environ.get("BCE_ACCESS_KEY_ID")
        secret_key = os.environ.get("BCE_SECRET_ACCESS_KEY")
        session_token = os.environ.get("BCE_SESSION_TOKEN")
    if not access_key or not secret_key:
        raise ValueError(
            "Set BCE_ACCESS_KEY_ID and BCE_SECRET_ACCESS_KEY, or use an owner-only "
            "--credentials-file; never pass credentials on the command line"
        )
    regions = _parse_regions(args.regions)
    endpoints = _parse_endpoints(args.endpoint or [])
    requested_vpcs = _parse_csv(args.vpc_ids)
    inventory = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": utc_now(),
        "mode": "live",
        "regions": {},
    }
    for region in regions:
        endpoint = endpoints.get(region, f"https://bcc.{region}.baidubce.com")
        inventory["regions"][region] = collect_region(
            region,
            endpoint,
            access_key,
            secret_key,
            session_token,
            args.timeout,
            args.max_retries,
            requested_vpcs,
        )
    return inventory


def load_inventory(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        inventory = json.load(handle)
    if not isinstance(inventory, dict) or not isinstance(inventory.get("regions"), dict):
        raise ValueError("Inventory must be a JSON object with a regions object")
    inventory.setdefault("schemaVersion", SCHEMA_VERSION)
    inventory.setdefault("mode", "offline")
    for region_data in inventory["regions"].values():
        if not isinstance(region_data, dict):
            raise ValueError("Each region must be a JSON object")
        resources = region_data.setdefault("resources", {})
        coverage = region_data.setdefault("coverage", {})
        region_data.setdefault("errors", [])
        for key in RESOURCE_KEYS:
            resources.setdefault(key, [])
            coverage.setdefault(key, {"status": "unknown", "count": len(resources[key])})
    return inventory


def _protocol(value: Any) -> str:
    text = str(value or "all").strip().lower()
    return "all" if text in {"", "any", "-1"} else text


def _action(value: Any, *, default: str = "allow") -> str:
    return str(value or default).strip().lower()


def _parse_ports(value: Any, protocol: str) -> list[tuple[int, int]] | None:
    if protocol in {"all", "icmp", "icmpv6"}:
        return [(1, 65535)]
    text = str(value or "1-65535").strip().lower().replace(" ", "")
    if text in {"", "all", "any", "0-65535", "1-65535", "-1"}:
        return [(1, 65535)]
    intervals: list[tuple[int, int]] = []
    try:
        for part in text.split(","):
            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start, end = int(start_text), int(end_text)
            else:
                start = end = int(part)
            if start == 0:
                start = 1
            if start < 1 or end > 65535 or start > end:
                return None
            intervals.append((start, end))
    except ValueError:
        return None
    return intervals


def _ports_all(intervals: list[tuple[int, int]] | None) -> bool:
    return bool(intervals) and any(start <= 1 and end >= 65535 for start, end in intervals)


def _sensitive_ports(intervals: list[tuple[int, int]] | None) -> list[int]:
    if intervals is None:
        return []
    return sorted(
        port for port in SENSITIVE_PORTS if any(start <= port <= end for start, end in intervals)
    )


def _public_address(value: Any) -> bool:
    text = str(value or "").strip().lower()
    if text in {"all", "any", "0.0.0.0/0", "::/0"}:
        return True
    try:
        network = ipaddress.ip_network(text, strict=False)
        return network.prefixlen == 0
    except ValueError:
        return False


def _remote(rule: dict[str, Any], kind: str) -> tuple[str | None, str]:
    direction = str(rule.get("direction") or "").lower()
    if kind == "acl":
        field = "sourceIpAddress" if direction == "ingress" else "destinationIpAddress"
        value = rule.get(field)
        return (str(value) if value not in (None, "") else None, field)
    field = "sourceIp" if direction == "ingress" else "destIp"
    value = rule.get(field)
    if value not in (None, ""):
        return str(value), field
    group_field = "sourceGroupId" if direction == "ingress" else "destGroupId"
    if rule.get(group_field):
        return None, group_field
    if rule.get("remoteIpSet"):
        return None, "remoteIpSet"
    if rule.get("remoteIpGroup"):
        return None, "remoteIpGroup"
    return None, field


def _rule_id(rule: dict[str, Any], kind: str) -> str | None:
    if kind == "sg":
        return _resource_id(rule, "securityGroupRuleId", "id")
    if kind == "esg":
        return _resource_id(rule, "enterpriseSecurityGroupRuleId", "id")
    return _resource_id(rule, "id", "aclRuleId")


def _finding(
    rule_id: str,
    severity: str,
    region: str,
    resource_type: str,
    group_id: str | None,
    cloud_rule_id: str | None,
    fact: str,
    interpretation: str,
    *,
    vpc_id: str | None = None,
    subnet_id: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ruleId": rule_id,
        "severity": severity,
        "region": region,
        "resourceType": resource_type,
        "groupId": group_id,
        "cloudRuleId": cloud_rule_id,
        "vpcId": vpc_id,
        "subnetId": subnet_id,
        "fact": fact,
        "interpretation": interpretation,
        "evidence": evidence or {},
    }


def _rule_evidence(rule: dict[str, Any], kind: str) -> dict[str, Any]:
    remote, remote_field = _remote(rule, kind)
    port_field = "destinationPort" if kind == "acl" else "portRange"
    evidence = {
        "direction": rule.get("direction"),
        "action": _action(rule.get("action")),
        "networkType": rule.get("ipVersion") if kind == "acl" else rule.get("ethertype"),
        "protocol": rule.get("protocol"),
        "remoteField": remote_field,
        "remote": remote,
        "port": rule.get(port_field),
    }
    if kind == "esg":
        evidence["priority"] = rule.get("priority")
    if kind == "acl":
        evidence["position"] = rule.get("position")
        evidence["sourceIpAddress"] = rule.get("sourceIpAddress")
        evidence["destinationIpAddress"] = rule.get("destinationIpAddress")
        evidence["sourcePort"] = rule.get("sourcePort")
    return {key: value for key, value in evidence.items() if value is not None}


def _canonical_rule(rule: dict[str, Any], kind: str, *, include_action: bool = True) -> tuple[Any, ...]:
    remote, remote_field = _remote(rule, kind)
    port_field = "destinationPort" if kind == "acl" else "portRange"
    values: list[Any] = [
        str(rule.get("direction") or "").lower(),
        (
            str(rule.get("ipVersion") or 4)
            if kind == "acl"
            else str(rule.get("ethertype") or "IPv4").lower()
        ),
        _protocol(rule.get("protocol")),
        remote_field,
        str(remote or ""),
        str(rule.get(port_field) or ""),
    ]
    if kind == "acl":
        values.extend(
            [
                str(rule.get("sourceIpAddress") or ""),
                str(rule.get("destinationIpAddress") or ""),
                str(rule.get("sourcePort") or ""),
                str(rule.get("position") or ""),
            ]
        )
    if kind == "esg":
        values.extend([str(rule.get("localIp") or ""), str(rule.get("priority") or "")])
    if include_action:
        values.append(_action(rule.get("action")))
    return tuple(values)


def _audit_group(
    region: str,
    group: dict[str, Any],
    kind: str,
    prefix: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    group_id = _resource_id(group, "id", "securityGroupId", "enterpriseSecurityGroupId")
    vpc_id = _resource_id(group, "vpcId")
    rules = group.get("rules") if isinstance(group.get("rules"), list) else []
    resource_type = "ordinarySecurityGroup" if kind == "sg" else "enterpriseSecurityGroup"
    if not rules:
        findings.append(
            _finding(
                f"{prefix}-005",
                "info",
                region,
                resource_type,
                group_id,
                None,
                "安全组未返回任何规则",
                "平台语义为入站和出站均拒绝；确认是否符合业务意图",
                vpc_id=vpc_id,
            )
        )
        return findings

    seen: dict[tuple[Any, ...], str | None] = {}
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        cloud_rule_id = _rule_id(rule, kind)
        canonical = _canonical_rule(rule, kind)
        if canonical in seen:
            findings.append(
                _finding(
                    f"{prefix}-006",
                    "low",
                    region,
                    resource_type,
                    group_id,
                    cloud_rule_id,
                    f"规则与 {seen[canonical] or '另一条规则'} 的匹配条件完全重复",
                    "重复规则增加维护复杂度；删除前需确认关联实例和变更窗口",
                    vpc_id=vpc_id,
                    evidence=_rule_evidence(rule, kind),
                )
            )
        else:
            seen[canonical] = cloud_rule_id

        direction = str(rule.get("direction") or "").lower()
        action = _action(rule.get("action"), default="allow")
        protocol = _protocol(rule.get("protocol"))
        ports = _parse_ports(rule.get("portRange"), protocol)
        remote, _ = _remote(rule, kind)
        is_public = _public_address(remote)
        evidence = _rule_evidence(rule, kind)
        if action != "allow" or not is_public:
            continue
        if direction == "ingress":
            sensitive = (
                _sensitive_ports(ports) if protocol in {"tcp", "udp", "all"} else []
            )
            if protocol == "all" and _ports_all(ports):
                suffix, severity = "001", "high"
                fact = "公网来源被允许访问全部协议和全部端口"
                interpretation = "该规则形成最大范围的安全组入站暴露"
            elif sensitive:
                suffix, severity = "002", "high"
                fact = "公网来源被允许访问敏感目的端口：" + ", ".join(map(str, sensitive))
                interpretation = "管理面或数据服务可能暴露；仍需结合公网入口和监听状态确认可达性"
                evidence["sensitivePorts"] = sensitive
            else:
                suffix, severity = "003", "medium"
                fact = "入站允许规则的远端地址为公网全范围"
                interpretation = "来源范围过宽，需要确认是否为预期公开服务"
            findings.append(
                _finding(
                    f"{prefix}-{suffix}",
                    severity,
                    region,
                    resource_type,
                    group_id,
                    cloud_rule_id,
                    fact,
                    interpretation,
                    vpc_id=vpc_id,
                    evidence=evidence,
                )
            )
        elif direction == "egress" and protocol == "all" and _ports_all(ports):
            findings.append(
                _finding(
                    f"{prefix}-004",
                    "low",
                    region,
                    resource_type,
                    group_id,
                    cloud_rule_id,
                    "出站允许全部协议、全部端口和全部远端地址",
                    "常见默认规则；作为最小权限治理项复核，不据此判断存在数据泄露",
                    vpc_id=vpc_id,
                    evidence=evidence,
                )
            )

    if kind == "esg":
        by_match: dict[tuple[Any, ...], dict[str, str | None]] = {}
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            key = _canonical_rule(rule, kind, include_action=False)
            action = _action(rule.get("action"))
            by_match.setdefault(key, {})[action] = _rule_id(rule, kind)
        for key, actions in by_match.items():
            if "allow" in actions and "deny" in actions:
                findings.append(
                    _finding(
                        "ESG-007",
                        "medium",
                        region,
                        resource_type,
                        group_id,
                        actions.get("allow"),
                        "同一优先级和匹配条件同时存在 allow 与 deny",
                        "百度智能云在同优先级下以 deny 优先；确认配置意图并避免误判",
                        vpc_id=vpc_id,
                        evidence={
                            "allowRuleId": actions.get("allow"),
                            "denyRuleId": actions.get("deny"),
                            "match": list(key),
                        },
                    )
                )
    return findings


def _network_covers(earlier: Any, later: Any) -> bool | None:
    first = str(earlier or "").strip().lower()
    second = str(later or "").strip().lower()
    if first in {"all", "any"}:
        return True
    if not first or not second:
        return None
    try:
        first_network = ipaddress.ip_network(first, strict=False)
        second_network = ipaddress.ip_network(second, strict=False)
    except ValueError:
        return first == second if first == second else None
    if first_network.version != second_network.version:
        return False
    return first_network == second_network or first_network.supernet_of(second_network)


def _ports_cover(
    earlier: list[tuple[int, int]] | None,
    later: list[tuple[int, int]] | None,
) -> bool | None:
    if earlier is None or later is None:
        return None
    return all(
        any(first_start <= second_start and first_end >= second_end for first_start, first_end in earlier)
        for second_start, second_end in later
    )


def _acl_covers(earlier: dict[str, Any], later: dict[str, Any]) -> bool:
    if str(earlier.get("direction") or "").lower() != str(later.get("direction") or "").lower():
        return False
    if str(earlier.get("ipVersion") or 4) != str(later.get("ipVersion") or 4):
        return False
    first_protocol = _protocol(earlier.get("protocol"))
    second_protocol = _protocol(later.get("protocol"))
    if first_protocol != "all" and first_protocol != second_protocol:
        return False
    checks = [
        _network_covers(earlier.get("sourceIpAddress"), later.get("sourceIpAddress")),
        _network_covers(
            earlier.get("destinationIpAddress"), later.get("destinationIpAddress")
        ),
        _ports_cover(
            _parse_ports(earlier.get("sourcePort"), first_protocol),
            _parse_ports(later.get("sourcePort"), second_protocol),
        ),
        _ports_cover(
            _parse_ports(earlier.get("destinationPort"), first_protocol),
            _parse_ports(later.get("destinationPort"), second_protocol),
        ),
    ]
    return all(value is True for value in checks)


def _position(rule: dict[str, Any]) -> int | None:
    try:
        return int(rule.get("position"))
    except (TypeError, ValueError):
        return None


def _audit_acl(region: str, entry: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    vpc_id = _resource_id(entry, "vpcId")
    subnet_id = _resource_id(entry, "subnetId", "id")
    rules = entry.get("aclRules") if isinstance(entry.get("aclRules"), list) else []
    seen: dict[tuple[Any, ...], str | None] = {}
    valid_rules = [rule for rule in rules if isinstance(rule, dict)]
    for rule in valid_rules:
        cloud_rule_id = _rule_id(rule, "acl")
        canonical = _canonical_rule(rule, "acl")
        if canonical in seen:
            findings.append(
                _finding(
                    "ACL-005",
                    "low",
                    region,
                    "acl",
                    subnet_id,
                    cloud_rule_id,
                    f"ACL 规则与 {seen[canonical] or '另一条规则'} 完全重复",
                    "重复规则增加维护复杂度；调整前需验证业务流量",
                    vpc_id=vpc_id,
                    subnet_id=subnet_id,
                    evidence=_rule_evidence(rule, "acl"),
                )
            )
        else:
            seen[canonical] = cloud_rule_id

        direction = str(rule.get("direction") or "").lower()
        action = _action(rule.get("action"))
        protocol = _protocol(rule.get("protocol"))
        ports = _parse_ports(rule.get("destinationPort"), protocol)
        remote, _ = _remote(rule, "acl")
        evidence = _rule_evidence(rule, "acl")
        if action != "allow" or not _public_address(remote):
            continue
        if direction == "ingress":
            sensitive = (
                _sensitive_ports(ports) if protocol in {"tcp", "udp", "all"} else []
            )
            if protocol == "all" and _ports_all(ports):
                code, severity = "ACL-001", "high"
                fact = "ACL 允许公网来源访问全部协议和全部端口"
                interpretation = "该规则形成最大范围的子网入站暴露"
            elif sensitive:
                code, severity = "ACL-002", "high"
                fact = "ACL 允许公网来源访问敏感目的端口：" + ", ".join(map(str, sensitive))
                interpretation = "子网边界允许敏感服务流量；需结合安全组和实例监听确认"
                evidence["sensitivePorts"] = sensitive
            else:
                code, severity = "ACL-003", "medium"
                fact = "ACL 入站允许规则的来源为公网全范围"
                interpretation = "来源范围过宽，需要确认是否为预期公开服务"
            findings.append(
                _finding(
                    code,
                    severity,
                    region,
                    "acl",
                    subnet_id,
                    cloud_rule_id,
                    fact,
                    interpretation,
                    vpc_id=vpc_id,
                    subnet_id=subnet_id,
                    evidence=evidence,
                )
            )
        elif direction == "egress" and protocol == "all" and _ports_all(ports):
            findings.append(
                _finding(
                    "ACL-004",
                    "low",
                    region,
                    "acl",
                    subnet_id,
                    cloud_rule_id,
                    "ACL 出站允许全部协议、全部端口和全部远端地址",
                    "作为最小权限治理项复核，不据此判断存在数据泄露",
                    vpc_id=vpc_id,
                    subnet_id=subnet_id,
                    evidence=evidence,
                )
            )

    ordered = sorted(
        (rule for rule in valid_rules if _position(rule) is not None),
        key=lambda item: _position(item) or 0,
    )
    for index, later in enumerate(ordered):
        for earlier in ordered[:index]:
            if not _acl_covers(earlier, later):
                continue
            same_action = _action(earlier.get("action")) == _action(later.get("action"))
            findings.append(
                _finding(
                    "ACL-006" if same_action else "ACL-007",
                    "low" if same_action else "medium",
                    region,
                    "acl",
                    subnet_id,
                    _rule_id(later, "acl"),
                    (
                        "较高优先级 ACL 规则完全覆盖该规则，且动作相同"
                        if same_action
                        else "较高优先级 ACL 规则完全覆盖该规则，但动作相反"
                    ),
                    (
                        "较低优先级规则可能冗余"
                        if same_action
                        else "较低优先级规则可能永远不生效，需核对策略意图"
                    ),
                    vpc_id=vpc_id,
                    subnet_id=subnet_id,
                    evidence={
                        "earlierRuleId": _rule_id(earlier, "acl"),
                        "earlierPosition": _position(earlier),
                        "earlierAction": _action(earlier.get("action")),
                        "laterPosition": _position(later),
                        "laterAction": _action(later.get("action")),
                    },
                )
            )
            break
    return findings


def analyze_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    totals = {
        "vpcs": 0,
        "securityGroups": 0,
        "securityGroupRules": 0,
        "enterpriseSecurityGroups": 0,
        "enterpriseSecurityGroupRules": 0,
        "aclEntries": 0,
        "aclRules": 0,
    }
    for region, region_data in inventory.get("regions", {}).items():
        resources = region_data.get("resources", {})
        vpcs = resources.get("vpcs", [])
        groups = resources.get("securityGroups", [])
        enterprise_groups = resources.get("enterpriseSecurityGroups", [])
        acls = resources.get("acls", [])
        totals["vpcs"] += len(vpcs)
        totals["securityGroups"] += len(groups)
        totals["enterpriseSecurityGroups"] += len(enterprise_groups)
        totals["aclEntries"] += len(acls)
        totals["securityGroupRules"] += sum(
            len(item.get("rules", [])) for item in groups if isinstance(item, dict)
        )
        totals["enterpriseSecurityGroupRules"] += sum(
            len(item.get("rules", [])) for item in enterprise_groups if isinstance(item, dict)
        )
        totals["aclRules"] += sum(
            len(item.get("aclRules", [])) for item in acls if isinstance(item, dict)
        )
        for error in region_data.get("errors", []):
            status = error.get("status")
            findings.append(
                _finding(
                    "COV-002" if status in (401, 403) else "COV-001",
                    "high",
                    region,
                    str(error.get("resourceType") or "unknown"),
                    error.get("scope"),
                    None,
                    f"采集失败，状态为 {status or 'network-error'}",
                    "该资源类型覆盖不完整，不能据此判断没有风险规则",
                    evidence={
                        key: error.get(key)
                        for key in ("status", "code", "requestId", "path", "scope")
                        if error.get(key) is not None
                    },
                )
            )
        for group in groups:
            if isinstance(group, dict):
                findings.extend(_audit_group(region, group, "sg", "SG"))
        for group in enterprise_groups:
            if isinstance(group, dict):
                findings.extend(_audit_group(region, group, "esg", "ESG"))
        for entry in acls:
            if isinstance(entry, dict):
                findings.extend(_audit_acl(region, entry))
    findings.sort(
        key=lambda item: (
            SEVERITY_ORDER.get(item["severity"], 9),
            item["region"],
            item["ruleId"],
            str(item.get("groupId") or ""),
            str(item.get("cloudRuleId") or ""),
        )
    )
    return {
        "generatedAt": utc_now(),
        "sourceGeneratedAt": inventory.get("generatedAt"),
        "totals": totals,
        "findingCounts": {
            severity: sum(1 for item in findings if item["severity"] == severity)
            for severity in ("high", "medium", "low", "info")
        },
        "findings": findings,
    }


def _md(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(inventory: dict[str, Any], analysis: dict[str, Any]) -> str:
    lines = [
        "# 百度智能云 VPC 安全组与 ACL 巡检报告",
        "",
        f"- 快照时间：{_md(inventory.get('generatedAt'))}",
        f"- 报告时间：{_md(analysis.get('generatedAt'))}",
        f"- 模式：{_md(inventory.get('mode'))}",
        f"- 地域：{', '.join(sorted(inventory.get('regions', {})))}",
        "- 安全边界：仅执行 GET 查询；未执行任何云资源变更。",
        "",
        "## 采集覆盖率",
        "",
        "| 地域 | 资源类型 | 状态 | 数量 | 查询数 | 失败查询数 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for region, region_data in sorted(inventory.get("regions", {}).items()):
        for resource_type in RESOURCE_KEYS:
            coverage = region_data.get("coverage", {}).get(resource_type, {})
            lines.append(
                "| {} | {} | {} | {} | {} | {} |".format(
                    _md(region),
                    _md(resource_type),
                    _md(coverage.get("status", "unknown")),
                    _md(coverage.get("count", 0)),
                    _md(coverage.get("queries", "-")),
                    _md(coverage.get("failedQueries", "-")),
                )
            )
    totals = analysis.get("totals", {})
    lines.extend(
        [
            "",
            "## 策略汇总",
            "",
            "| VPC | 普通安全组 | 普通规则 | 企业安全组 | 企业规则 | ACL 条目 | ACL 规则 |",
            "|---:|---:|---:|---:|---:|---:|---:|",
            "| {} | {} | {} | {} | {} | {} | {} |".format(
                totals.get("vpcs", 0),
                totals.get("securityGroups", 0),
                totals.get("securityGroupRules", 0),
                totals.get("enterpriseSecurityGroups", 0),
                totals.get("enterpriseSecurityGroupRules", 0),
                totals.get("aclEntries", 0),
                totals.get("aclRules", 0),
            ),
        ]
    )
    counts = analysis.get("findingCounts", {})
    lines.extend(
        [
            "",
            "## 发现",
            "",
            f"高：{counts.get('high', 0)}；中：{counts.get('medium', 0)}；低：{counts.get('low', 0)}；信息：{counts.get('info', 0)}。",
            "",
            "| 严重度 | 规则 | 地域 | 策略 | 云规则 | VPC/子网 | 事实 | 判断 |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for finding in analysis.get("findings", []):
        scope = "/".join(
            value for value in (finding.get("vpcId"), finding.get("subnetId")) if value
        ) or "-"
        lines.append(
            "| {} | {} | {} | {}:{} | {} | {} | {} | {} |".format(
                _md(finding.get("severity")),
                _md(finding.get("ruleId")),
                _md(finding.get("region")),
                _md(finding.get("resourceType")),
                _md(finding.get("groupId")),
                _md(finding.get("cloudRuleId")),
                _md(scope),
                _md(finding.get("fact")),
                _md(finding.get("interpretation")),
            )
        )
    lines.extend(
        [
            "",
            "## 结论限制",
            "",
            "- 安全策略允许不等于端到端公网可达；公网 IP、路由、监听服务和主机防火墙不在本报告范围内。",
            "- 地址组、参数模板、地址族和嵌套安全组未展开时，不将其成员推断为公网。",
            "- 宽泛出站、重复和遮蔽规则需要结合业务流量人工确认，不应直接自动删除。",
            "- 若覆盖率不是全部成功，本报告仅代表已成功查询的范围。",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    output_dir: Path,
    inventory: dict[str, Any],
    analysis: dict[str, Any],
    *,
    overwrite: bool,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory_path = output_dir / "inventory.json"
    report_path = output_dir / "report.md"
    if not overwrite:
        existing = [path for path in (inventory_path, report_path) if path.exists()]
        if existing:
            raise FileExistsError(
                "Refusing to overwrite existing output: " + ", ".join(str(path) for path in existing)
            )
    payload = dict(inventory)
    payload["analysis"] = analysis
    with inventory_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(inventory, analysis))
    return inventory_path, report_path


def self_test() -> None:
    sample = Path(__file__).resolve().parents[1] / "examples" / "sample-security-policies.json"
    inventory = load_inventory(sample)
    analysis = analyze_inventory(inventory)
    rule_ids = {item["ruleId"] for item in analysis["findings"]}
    expected = {"SG-001", "ESG-007", "ACL-002", "ACL-007"}
    missing = expected - rule_ids
    if missing:
        raise AssertionError(f"Sample analysis missed expected rules: {sorted(missing)}")

    family_fixture = {
        "schemaVersion": SCHEMA_VERSION,
        "regions": {
            "bj": {
                "coverage": {key: {"status": "success"} for key in RESOURCE_KEYS},
                "resources": {
                    "vpcs": [{"vpcId": "vpc-family"}],
                    "securityGroups": [
                        {
                            "id": "g-family",
                            "rules": [
                                {
                                    "securityGroupRuleId": "r-v4",
                                    "direction": "egress",
                                    "ethertype": "IPv4",
                                    "protocol": "all",
                                    "destIp": "all",
                                    "portRange": "1-65535",
                                },
                                {
                                    "securityGroupRuleId": "r-v6",
                                    "direction": "egress",
                                    "ethertype": "IPv6",
                                    "protocol": "all",
                                    "destIp": "all",
                                    "portRange": "1-65535",
                                },
                                {
                                    "securityGroupRuleId": "r-icmp",
                                    "direction": "ingress",
                                    "ethertype": "IPv4",
                                    "protocol": "icmp",
                                    "sourceIp": "all",
                                },
                            ],
                        }
                    ],
                    "enterpriseSecurityGroups": [],
                    "acls": [
                        {
                            "vpcId": "vpc-family",
                            "subnetId": "sbn-family",
                            "aclRules": [
                                {
                                    "id": "ar-v4",
                                    "direction": "ingress",
                                    "ipVersion": 4,
                                    "protocol": "all",
                                    "sourceIpAddress": "all",
                                    "destinationIpAddress": "all",
                                    "sourcePort": "all",
                                    "destinationPort": "all",
                                    "position": 100,
                                    "action": "allow",
                                },
                                {
                                    "id": "ar-v6",
                                    "direction": "ingress",
                                    "ipVersion": 6,
                                    "protocol": "all",
                                    "sourceIpAddress": "all",
                                    "destinationIpAddress": "all",
                                    "sourcePort": "all",
                                    "destinationPort": "all",
                                    "position": 200,
                                    "action": "allow",
                                },
                            ],
                        }
                    ],
                },
                "errors": [],
            }
        },
    }
    family_findings = analyze_inventory(family_fixture)["findings"]
    if any(item["ruleId"] == "SG-006" for item in family_findings):
        raise AssertionError("IPv4 and IPv6 security-group rules were treated as duplicates")
    if any(
        item["ruleId"] == "SG-002" and item.get("cloudRuleId") == "r-icmp"
        for item in family_findings
    ):
        raise AssertionError("ICMP rule was incorrectly evaluated as a sensitive-port rule")
    if any(item["ruleId"] in {"ACL-006", "ACL-007"} for item in family_findings):
        raise AssertionError("IPv4 ACL rule was incorrectly treated as covering IPv6")

    client = ReadOnlyBceClient("https://bcc.bj.baidubce.com", "ak", "sk")
    try:
        client.request_json("/v2/securityGroup", method="POST")
    except ValueError as exc:
        if "non-GET" not in str(exc):
            raise
    else:
        raise AssertionError("Read-only guard did not reject POST")
    try:
        ReadOnlyBceClient("https://example.com", "ak", "sk")
    except ValueError as exc:
        if "baidubce.com" not in str(exc):
            raise
    else:
        raise AssertionError("Endpoint guard accepted an untrusted host")

    page_calls = []
    def fake_pages(path: str, params: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
        page_calls.append((path, dict(params or {})))
        if params and params.get("marker") == "page-2":
            return {"securityGroups": [{"id": "g-2"}], "isTruncated": False}
        return {
            "securityGroups": [{"id": "g-1"}],
            "isTruncated": True,
            "nextMarker": "page-2",
        }
    client.request_json = fake_pages  # type: ignore[method-assign]
    paged = client.paginate("/v2/securityGroup", ("securityGroups",))
    if [item.get("id") for item in paged] != ["g-1", "g-2"] or len(page_calls) != 2:
        raise AssertionError("Pagination did not collect both pages exactly once")

    authorization, headers = bce_authorization(
        "test-ak",
        "test-sk",
        "bcc.bj.baidubce.com",
        "/v1/vpc",
        {"maxKeys": 1000},
        timestamp="2026-08-13T08:00:00Z",
    )
    expected_signature = (
        "bce-auth-v1/test-ak/2026-08-13T08:00:00Z/1800/host;x-bce-date/"
        "cc1821bf523e9a38f8c086c48b2874f1555c7f672c4fa7ccd91e9d0de24dc889"
    )
    if authorization != expected_signature or headers.get("Authorization") != authorization:
        raise AssertionError("Signer output no longer matches the official SDK test vector")

    with tempfile.TemporaryDirectory() as temporary_dir:
        credentials_path = Path(temporary_dir) / "credentials.json"
        credentials_path.write_text(
            json.dumps({"accessKeyId": "file-ak", "secretAccessKey": "file-sk"}),
            encoding="utf-8",
        )
        credentials_path.chmod(0o600)
        if _read_credentials_file(credentials_path) != ("file-ak", "file-sk", None):
            raise AssertionError("Credentials file loader returned unexpected values")
        credentials_path.chmod(0o644)
        try:
            _read_credentials_file(credentials_path)
        except ValueError as exc:
            if "permissions" not in str(exc):
                raise
        else:
            raise AssertionError("Credentials file loader accepted broad permissions")
    print(
        "Self-test passed: fixture rules, GET-only and endpoint guards, pagination, "
        "credential-file guards, ACL shadowing, and deterministic signer"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only Baidu AI Cloud VPC security group and ACL audit"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--input", type=Path, help="Analyze an existing normalized inventory JSON")
    mode.add_argument("--self-test", action="store_true", help="Run local tests without network access")
    parser.add_argument("--regions", help="Comma-separated BCE region codes for live collection")
    parser.add_argument("--vpc-ids", help="Optional comma-separated VPC IDs to audit")
    parser.add_argument(
        "--credentials-file",
        type=Path,
        help="Owner-only (chmod 600) JSON credential file outside the Skill package",
    )
    parser.add_argument(
        "--endpoint",
        action="append",
        help="HTTPS endpoint override in REGION=https://host form; may be repeated",
    )
    parser.add_argument("--output-dir", type=Path, help="Directory for inventory.json and report.md")
    parser.add_argument("--timeout", type=float, default=20.0, help="Per-request timeout in seconds")
    parser.add_argument("--max-retries", type=int, default=3, help="GET retry count for 429 and 5xx")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing existing output files")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        if not args.output_dir:
            parser.error("--output-dir is required unless --self-test is used")
        inventory = load_inventory(args.input) if args.input else collect_live(args)
        analysis = analyze_inventory(inventory)
        inventory_path, report_path = write_outputs(
            args.output_dir, inventory, analysis, overwrite=args.overwrite
        )
        print(f"Inventory: {inventory_path}")
        print(f"Report: {report_path}")
        required = ("securityGroups", "enterpriseSecurityGroups", "acls")
        incomplete = any(
            region_data.get("coverage", {}).get(key, {}).get("status") != "success"
            for region_data in inventory.get("regions", {}).values()
            for key in required
        )
        return 2 if incomplete else 0
    except (ApiFailure, FileExistsError, OSError, ValueError, AssertionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
