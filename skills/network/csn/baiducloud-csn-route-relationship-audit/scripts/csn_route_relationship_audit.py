#!/usr/bin/env python3
"""Read-only Baidu AI Cloud CSN route-relationship audit."""

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
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
ENDPOINT = "https://csn.baidubce.com"
HOST = "csn.baidubce.com"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
ROUTE_TABLE_TYPES = {"default", "custom"}
INSTANCE_TYPES = {"vpc", "channel", "bec_vpc"}
NORMAL_ASSOCIATION_STATUSES = {"active"}
NORMAL_PROPAGATION_STATUSES = {"enable", "enabled", "active"}
TRANSITIONAL_RELATIONSHIP_STATUSES = {
    "creating", "deleting", "enabling", "disabling", "pending", "updating"
}
ROUTE_STATUSES = {"active", "conflicted"}
ROUTE_TYPES = {"propagated", "custom"}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


class ApiFailure(RuntimeError):
    """Sanitized API failure without authorization material."""

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

    def to_dict(
        self,
        operation: str,
        scope: str | None = None,
        parent_csn_id: str | None = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "operation": operation,
            "status": self.status,
            "code": self.code,
            "message": self.message,
            "requestId": self.request_id,
            "path": self.path,
            "scope": scope,
            "parentCsnId": parent_csn_id,
        }
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
    signed = {"host": HOST, "x-bce-date": timestamp}
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
    result = {
        "Host": HOST,
        "x-bce-date": timestamp,
        "Authorization": f"{auth_prefix}/{';'.join(signed_names)}/{signature}",
        "Accept": "application/json",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "baiducloud-csn-route-relationship-audit/1.0",
    }
    if session_token:
        result["x-bce-security-token"] = session_token
    return result


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
        url = f"{ENDPOINT}{path}"
        if query:
            url = f"{url}?{query}"
        for attempt in range(self.max_retries + 1):
            timestamp = utc_now()
            headers = bce_headers(
                self.access_key,
                self.secret_key,
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
        query_count = 0
        while True:
            if marker:
                query["marker"] = marker
            response = self.request_json(path, query)
            query_count += 1
            items.extend(item for item in _first_list(response, item_fields) if isinstance(item, dict))
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
        return items, query_count


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


def _parse_requested_ids(value: str | None) -> list[str]:
    result: list[str] = []
    for raw in (value or "").split(","):
        item = raw.strip()
        if not item:
            continue
        if not all(character.isalnum() or character in "-_" for character in item):
            raise ValueError(f"Invalid CSN ID: {item}")
        if item not in result:
            result.append(item)
    return result


def _aggregate_status(success: int, failed: int, skipped: int = 0, blocked: int = 0) -> str:
    incomplete = failed + skipped + blocked
    if incomplete:
        return "failed" if success == 0 else "partial"
    return "success"


def _child_coverage() -> dict[str, Any]:
    return {
        "status": "pending",
        "successfulRouteTables": 0,
        "failedRouteTables": 0,
        "skippedRouteTables": 0,
        "blockedCsns": 0,
        "queries": 0,
    }


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
    client = ReadOnlyBceClient(
        access_key, secret_key, session_token,
        timeout=args.timeout, max_retries=args.max_retries,
    )
    requested_ids = _parse_requested_ids(args.csn_ids)
    inventory: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": utc_now(),
        "mode": "live",
        "endpoint": ENDPOINT,
        "selection": {"requestedCsnIds": requested_ids, "unmatchedCsnIds": []},
        "coverage": {
            "listCsns": {"status": "pending", "count": 0, "queries": 0, "failedQueries": 0},
            "listInstances": {
                "status": "pending", "successfulCsns": 0, "failedCsns": 0,
                "queries": 0, "instanceCount": 0,
            },
            "listRouteTables": {
                "status": "pending", "successfulCsns": 0, "failedCsns": 0,
                "queries": 0, "routeTableCount": 0,
            },
            "listAssociations": _child_coverage(),
            "listPropagations": _child_coverage(),
            "listRules": _child_coverage(),
        },
        "csns": [],
        "errors": [],
    }
    inventory["coverage"]["listAssociations"]["associationCount"] = 0
    inventory["coverage"]["listPropagations"]["propagationCount"] = 0
    inventory["coverage"]["listRules"]["routeRuleCount"] = 0
    try:
        summaries, query_count = client.paginate("/v1/csn", ("csns",))
        inventory["coverage"]["listCsns"].update(
            status="success", count=len(summaries), queries=query_count
        )
    except ApiFailure as exc:
        inventory["coverage"]["listCsns"].update(
            status="failed", queries=1, failedQueries=1
        )
        for key in ("listInstances", "listRouteTables", "listAssociations", "listPropagations", "listRules"):
            inventory["coverage"][key]["status"] = "blocked"
        inventory["errors"].append(exc.to_dict("listCsns"))
        return inventory

    if requested_ids:
        visible_ids = {_optional_string(item.get("csnId")) for item in summaries}
        inventory["selection"]["unmatchedCsnIds"] = [
            item for item in requested_ids if item not in visible_ids
        ]
        selected = [item for item in summaries if _optional_string(item.get("csnId")) in requested_ids]
    else:
        selected = summaries

    instance_cov = inventory["coverage"]["listInstances"]
    table_cov = inventory["coverage"]["listRouteTables"]
    association_cov = inventory["coverage"]["listAssociations"]
    propagation_cov = inventory["coverage"]["listPropagations"]
    rule_cov = inventory["coverage"]["listRules"]

    for summary in selected:
        csn = dict(summary)
        csn["instances"] = []
        csn["routeTables"] = []
        csn_id = _optional_string(summary.get("csnId"))
        if not csn_id:
            csn["_instancesStatus"] = "skipped"
            csn["_routeTablesStatus"] = "skipped"
            instance_cov["failedCsns"] += 1
            table_cov["failedCsns"] += 1
            for coverage in (association_cov, propagation_cov, rule_cov):
                coverage["blockedCsns"] += 1
            inventory["csns"].append(csn)
            continue

        instance_path = f"/v1/csn/{_quote(csn_id)}/instance"
        try:
            instances, count = client.paginate(instance_path, ("instances",))
            instance_cov["queries"] += count
            instance_cov["successfulCsns"] += 1
            instance_cov["instanceCount"] += len(instances)
            csn["instances"] = instances
            csn["_instancesStatus"] = "success"
        except ApiFailure as exc:
            instance_cov["failedCsns"] += 1
            csn["_instancesStatus"] = "failed"
            inventory["errors"].append(exc.to_dict("listInstances", csn_id, csn_id))

        table_path = f"/v1/csn/{_quote(csn_id)}/routeTable"
        try:
            route_tables, count = client.paginate(table_path, ("csnRts",))
            table_cov["queries"] += count
            table_cov["successfulCsns"] += 1
            table_cov["routeTableCount"] += len(route_tables)
            csn["_routeTablesStatus"] = "success"
        except ApiFailure as exc:
            table_cov["failedCsns"] += 1
            csn["_routeTablesStatus"] = "failed"
            for coverage in (association_cov, propagation_cov, rule_cov):
                coverage["blockedCsns"] += 1
            inventory["errors"].append(exc.to_dict("listRouteTables", csn_id, csn_id))
            inventory["csns"].append(csn)
            continue

        for table_summary in route_tables:
            table = dict(table_summary)
            table["associations"] = []
            table["propagations"] = []
            table["rules"] = []
            route_table_id = _optional_string(table.get("csnRtId"))
            if not route_table_id:
                table["_associationsStatus"] = "skipped"
                table["_propagationsStatus"] = "skipped"
                table["_rulesStatus"] = "skipped"
                for coverage in (association_cov, propagation_cov, rule_cov):
                    coverage["skippedRouteTables"] += 1
                csn["routeTables"].append(table)
                continue

            base_path = f"/v1/csn/routeTable/{_quote(route_table_id)}"
            for operation, suffix, field, status_field, coverage, count_field in (
                ("listAssociations", "/association", "associations", "_associationsStatus", association_cov, "associationCount"),
                ("listPropagations", "/propagation", "propagations", "_propagationsStatus", propagation_cov, "propagationCount"),
            ):
                coverage["queries"] += 1
                try:
                    response = client.request_json(base_path + suffix)
                    records = _first_list(response, (field,))
                    table[field] = [item for item in records if isinstance(item, dict)]
                    table[status_field] = "success"
                    coverage["successfulRouteTables"] += 1
                    coverage[count_field] += len(table[field])
                except ApiFailure as exc:
                    table[status_field] = "failed"
                    coverage["failedRouteTables"] += 1
                    inventory["errors"].append(
                        exc.to_dict(operation, route_table_id, csn_id)
                    )

            try:
                rules, count = client.paginate(base_path + "/rule", ("csnRtRules",))
                rule_cov["queries"] += count
                rule_cov["successfulRouteTables"] += 1
                rule_cov["routeRuleCount"] += len(rules)
                table["rules"] = rules
                table["_rulesStatus"] = "success"
            except ApiFailure as exc:
                rule_cov["failedRouteTables"] += 1
                table["_rulesStatus"] = "failed"
                inventory["errors"].append(
                    exc.to_dict("listRules", route_table_id, csn_id)
                )
            csn["routeTables"].append(table)
        inventory["csns"].append(csn)

    instance_cov["status"] = _aggregate_status(
        instance_cov["successfulCsns"], instance_cov["failedCsns"]
    )
    table_cov["status"] = _aggregate_status(
        table_cov["successfulCsns"], table_cov["failedCsns"]
    )
    for coverage in (association_cov, propagation_cov, rule_cov):
        coverage["status"] = _aggregate_status(
            coverage["successfulRouteTables"],
            coverage["failedRouteTables"],
            coverage["skippedRouteTables"],
            coverage["blockedCsns"],
        )
    return inventory


def load_inventory(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        inventory = json.load(handle)
    if not isinstance(inventory, dict) or not isinstance(inventory.get("csns"), list):
        raise ValueError("Inventory must be a JSON object containing a csns list")
    inventory.setdefault("schemaVersion", SCHEMA_VERSION)
    inventory.setdefault("generatedAt", utc_now())
    inventory["mode"] = "offline"
    inventory.setdefault("endpoint", "offline")
    inventory.setdefault("selection", {"requestedCsnIds": [], "unmatchedCsnIds": []})
    inventory.setdefault("coverage", {})
    inventory.setdefault("errors", [])
    for csn_index, csn in enumerate(inventory["csns"]):
        if not isinstance(csn, dict):
            raise ValueError(f"csns[{csn_index}] must be an object")
        if not isinstance(csn.setdefault("instances", []), list):
            raise ValueError(f"csns[{csn_index}].instances must be a list")
        if not isinstance(csn.setdefault("routeTables", []), list):
            raise ValueError(f"csns[{csn_index}].routeTables must be a list")
        csn.setdefault("_instancesStatus", "unknown")
        csn.setdefault("_routeTablesStatus", "unknown")
        for table_index, table in enumerate(csn["routeTables"]):
            if not isinstance(table, dict):
                raise ValueError(f"csns[{csn_index}].routeTables[{table_index}] must be an object")
            for field in ("associations", "propagations", "rules"):
                if not isinstance(table.setdefault(field, []), list):
                    raise ValueError(
                        f"csns[{csn_index}].routeTables[{table_index}].{field} must be a list"
                    )
            table.setdefault("_associationsStatus", "unknown")
            table.setdefault("_propagationsStatus", "unknown")
            table.setdefault("_rulesStatus", "unknown")
    return inventory


def _finding(
    rule_id: str,
    severity: str,
    csn: dict[str, Any] | None,
    table: dict[str, Any] | None,
    fact: str,
    interpretation: str,
    *,
    relationship: dict[str, Any] | None = None,
    rule: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    csn = csn or {}
    table = table or {}
    relationship = relationship or {}
    rule = rule or {}
    return {
        "ruleId": rule_id,
        "severity": severity,
        "csnId": _optional_string(csn.get("csnId")),
        "csnName": _optional_string(csn.get("name")),
        "csnRtId": _optional_string(table.get("csnRtId")),
        "routeTableName": _optional_string(table.get("name")),
        "attachId": _optional_string(relationship.get("attachId") or rule.get("fromAttachId")),
        "routeRuleId": _optional_string(rule.get("ruleId")),
        "fact": fact,
        "interpretation": interpretation,
        "evidence": evidence or {},
    }


def _relationship_status_finding(
    csn: dict[str, Any],
    table: dict[str, Any],
    relationship: dict[str, Any],
    kind: str,
    normal_statuses: set[str],
) -> dict[str, Any] | None:
    value = str(relationship.get("status") or "").strip().lower()
    if value in normal_statuses:
        return None
    if "fail" in value or "error" in value:
        severity = "high"
        interpretation = "控制面返回失败类状态，需要人工排查"
    elif value in TRANSITIONAL_RELATIONSHIP_STATUSES:
        severity = "info"
        interpretation = "关系处于过渡状态；缺少持续时间，不能判定卡住"
    else:
        severity = "info"
        interpretation = "状态缺失或不在当前文档示例中，需要人工解释"
    return _finding(
        "CSNREL-002", severity, csn, table,
        f"{kind}状态为 {value or 'missing'}", interpretation,
        relationship=relationship, evidence={"relationshipType": kind, "status": value or None},
    )


def _valid_network(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        ipaddress.ip_network(value.strip(), strict=False)
        return True
    except ValueError:
        return False


def analyze_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    csns = [item for item in inventory.get("csns", []) if isinstance(item, dict)]
    route_table_types: Counter[str] = Counter()
    association_statuses: Counter[str] = Counter()
    propagation_statuses: Counter[str] = Counter()
    route_statuses: Counter[str] = Counter()
    route_types: Counter[str] = Counter()
    route_regions: Counter[str] = Counter()
    total_instances = 0
    total_tables = 0
    total_associations = 0
    total_propagations = 0
    total_rules = 0

    for error in inventory.get("errors", []):
        if not isinstance(error, dict):
            continue
        status_code = error.get("status")
        rule_id = "COV-002" if status_code in (401, 403) else "COV-004" if status_code == 404 else "COV-001"
        severity = "info" if rule_id == "COV-004" else "high"
        csn_id = _optional_string(error.get("parentCsnId"))
        table_id = _optional_string(error.get("scope"))
        csn = next((item for item in csns if _optional_string(item.get("csnId")) == csn_id), None)
        table = None
        if csn:
            table = next(
                (item for item in csn.get("routeTables", []) if isinstance(item, dict) and _optional_string(item.get("csnRtId")) == table_id),
                None,
            )
        findings.append(
            _finding(
                rule_id, severity,
                csn or ({"csnId": csn_id} if csn_id else None),
                table or ({"csnRtId": table_id} if table_id and table_id != csn_id else None),
                f"{error.get('operation', 'query')} 查询失败，状态为 {status_code or 'network-error'}",
                "该范围的路由控制面覆盖不完整",
                evidence={
                    key: error.get(key)
                    for key in ("operation", "status", "code", "requestId", "path", "scope", "parentCsnId")
                    if error.get(key) is not None
                },
            )
        )

    for unmatched in inventory.get("selection", {}).get("unmatchedCsnIds", []):
        findings.append(
            _finding(
                "COV-001", "high", {"csnId": unmatched}, None,
                "指定的 CSN ID 未在成功取得的列表中匹配",
                "该指定范围未被审计；核对 ID 和当前账号可见性",
                evidence={"requestedCsnId": unmatched},
            )
        )

    for csn in csns:
        instances = [item for item in csn.get("instances", []) if isinstance(item, dict)]
        tables = [item for item in csn.get("routeTables", []) if isinstance(item, dict)]
        total_instances += len(instances)
        total_tables += len(tables)
        instance_by_attach = {
            str(item.get("attachId")): item for item in instances if str(item.get("attachId") or "")
        }

        if csn.get("_routeTablesStatus") == "success":
            ids: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
            for table in tables:
                route_table_id = str(table.get("csnRtId") or "")
                if route_table_id:
                    ids[route_table_id].append(table)
                else:
                    findings.append(
                        _finding("CSNRT-001", "high", csn, table, "路由表缺少 csnRtId", "无法安全查询或标识该路由表", evidence={"name": table.get("name"), "type": table.get("type")})
                    )
            for route_table_id, repeated in ids.items():
                if len(repeated) > 1:
                    findings.append(
                        _finding("CSNRT-001", "high", csn, repeated[0], "同一 CSN 重复返回相同 csnRtId", "路由表身份重复，需要核对列表或分页数据", evidence={"csnRtId": route_table_id, "occurrences": len(repeated)})
                    )
            default_tables = [table for table in tables if str(table.get("type") or "").lower() == "default"]
            if len(default_tables) != 1:
                findings.append(
                    _finding("CSNRT-003", "high", csn, default_tables[0] if default_tables else None, f"成功查询到 {len(default_tables)} 张 default 路由表", "产品指导说明 CSN 自动创建一张默认路由表，需要核对控制面结果", evidence={"defaultRouteTableCount": len(default_tables), "routeTableCount": len(tables)})
                )

        associated_tables: defaultdict[str, set[str]] = defaultdict(set)
        all_association_queries_success = csn.get("_routeTablesStatus") == "success" and all(
            table.get("_associationsStatus") == "success" for table in tables
        )
        all_propagation_queries_success = csn.get("_routeTablesStatus") == "success" and all(
            table.get("_propagationsStatus") == "success" for table in tables
        )
        propagated_attachments_all_tables: set[str] = set()
        associated_attachments_all_tables: set[str] = set()

        for table in tables:
            table_type = str(table.get("type") or "").strip().lower()
            route_table_types[table_type or "missing"] += 1
            if table_type not in ROUTE_TABLE_TYPES:
                findings.append(
                    _finding("CSNRT-002", "info", csn, table, f"路由表类型为 {table_type or 'missing'}", "类型缺失或不在当前官方枚举中，保留原始值", evidence={"type": table_type or None})
                )
            associations = [item for item in table.get("associations", []) if isinstance(item, dict)]
            propagations = [item for item in table.get("propagations", []) if isinstance(item, dict)]
            rules = [item for item in table.get("rules", []) if isinstance(item, dict)]
            if table.get("_associationsStatus") == "success":
                total_associations += len(associations)
            if table.get("_propagationsStatus") == "success":
                total_propagations += len(propagations)
            if table.get("_rulesStatus") == "success":
                total_rules += len(rules)
            if (
                table_type == "custom"
                and table.get("_associationsStatus") == "success"
                and table.get("_propagationsStatus") == "success"
                and table.get("_rulesStatus") == "success"
                and not associations and not propagations and not rules
            ):
                findings.append(
                    _finding("CSNRT-004", "info", csn, table, "自定义路由表没有关联、学习关系或路由条目", "路由表可能未使用、预留或用于有意隔离", evidence={"type": table_type})
                )

            for kind, records, status_field, normal_statuses in (
                ("关联关系", associations, "_associationsStatus", NORMAL_ASSOCIATION_STATUSES),
                ("学习关系", propagations, "_propagationsStatus", NORMAL_PROPAGATION_STATUSES),
            ):
                if table.get(status_field) != "success":
                    continue
                seen_attachments: Counter[str] = Counter()
                for relationship in records:
                    attach_id = str(relationship.get("attachId") or "")
                    status_value = str(relationship.get("status") or "").strip().lower()
                    if kind == "关联关系":
                        association_statuses[status_value or "missing"] += 1
                        if attach_id:
                            associated_tables[attach_id].add(str(table.get("csnRtId") or ""))
                            associated_attachments_all_tables.add(attach_id)
                    else:
                        propagation_statuses[status_value or "missing"] += 1
                        if attach_id:
                            propagated_attachments_all_tables.add(attach_id)
                    seen_attachments[attach_id] += 1
                    if not attach_id:
                        findings.append(
                            _finding("CSNREL-001", "high", csn, table, f"{kind}缺少 attachId", "关系无法对应到已加载网络实例", relationship=relationship, evidence={"relationshipType": kind})
                        )
                    elif csn.get("_instancesStatus") == "success" and attach_id not in instance_by_attach:
                        findings.append(
                            _finding("CSNREL-001", "high", csn, table, f"{kind}引用未出现在网络实例列表中的 attachId", "关系可能是孤立引用，或两次查询之间发生变化", relationship=relationship, evidence={"relationshipType": kind, "attachId": attach_id})
                        )
                    status_finding = _relationship_status_finding(
                        csn, table, relationship, kind, normal_statuses
                    )
                    if status_finding:
                        findings.append(status_finding)
                    loaded = instance_by_attach.get(attach_id)
                    if loaded:
                        mismatches: dict[str, Any] = {}
                        for field in ("instanceId", "instanceRegion", "instanceType"):
                            left = _optional_string(relationship.get(field))
                            right = _optional_string(loaded.get(field))
                            if left and right and left.lower() != right.lower():
                                mismatches[field] = {"relationship": left, "loadedInstance": right}
                        if mismatches:
                            findings.append(
                                _finding("CSNREL-007", "info", csn, table, f"{kind}元数据与网络实例列表不一致", "可能是查询期间变更或控制面元数据不同步", relationship=relationship, evidence={"mismatches": mismatches})
                            )
                for attach_id, count in seen_attachments.items():
                    if attach_id and count > 1:
                        sample = next(item for item in records if str(item.get("attachId") or "") == attach_id)
                        findings.append(
                            _finding("CSNREL-006", "medium", csn, table, f"同一路由表重复返回同一 attachId 的{kind}", "重复关系证据需要人工核对", relationship=sample, evidence={"relationshipType": kind, "attachId": attach_id, "occurrences": count})
                        )

            propagated_in_table = {
                str(item.get("attachId")) for item in propagations if str(item.get("attachId") or "")
            }
            rule_ids: Counter[str] = Counter()
            if table.get("_rulesStatus") == "success":
                for route in rules:
                    route_id = str(route.get("ruleId") or "")
                    destination = route.get("destAddress")
                    route_status = str(route.get("status") or "").strip().lower()
                    route_type = str(route.get("routeType") or "").strip().lower()
                    next_hop_region = str(route.get("nextHopRegion") or "").strip()
                    route_statuses[route_status or "missing"] += 1
                    route_types[route_type or "missing"] += 1
                    route_regions[next_hop_region or "missing"] += 1
                    rule_ids[route_id] += 1
                    if route_status == "conflicted":
                        findings.append(
                            _finding("CSNRULE-001", "high", csn, table, "路由状态为 conflicted", "该路由与先学习到的相同网段冲突，控制面标记其不生效", rule=route, evidence={"status": route_status, "destAddress": destination})
                        )
                    elif route_status not in ROUTE_STATUSES:
                        findings.append(
                            _finding("CSNRULE-008", "info", csn, table, f"路由状态为 {route_status or 'missing'}", "状态缺失或不在当前官方枚举中，需要人工解释", rule=route, evidence={"status": route_status or None})
                        )
                    if route.get("blackHole") is True:
                        findings.append(
                            _finding("CSNRULE-002", "medium", csn, table, "路由标记 blackHole=true", "匹配流量会被丢弃；可能是有意配置，需要核对意图", rule=route, evidence={"destAddress": destination, "blackHole": True})
                        )
                    missing = [field for field, value in (("ruleId", route_id), ("destAddress", destination)) if value in (None, "")]
                    if missing:
                        findings.append(
                            _finding("CSNRULE-003", "high", csn, table, f"路由缺少 {', '.join(missing)}", "路由身份或目标网段证据不完整", rule=route, evidence={"missingFields": missing})
                        )
                    elif not _valid_network(destination):
                        findings.append(
                            _finding("CSNRULE-004", "medium", csn, table, "路由目标不是有效的 IPv4/IPv6 网段", "目标网段语法需要人工核对", rule=route, evidence={"destAddress": destination})
                        )
                    parent_mismatch: dict[str, Any] = {}
                    returned_csn_id = _optional_string(route.get("csnId"))
                    returned_table_id = _optional_string(route.get("csnRtId"))
                    if returned_csn_id and returned_csn_id != _optional_string(csn.get("csnId")):
                        parent_mismatch["csnId"] = returned_csn_id
                    if returned_table_id and returned_table_id != _optional_string(table.get("csnRtId")):
                        parent_mismatch["csnRtId"] = returned_table_id
                    if parent_mismatch:
                        findings.append(
                            _finding("CSNRULE-005", "high", csn, table, "路由返回的父级 ID 与查询范围不一致", "CSN 或路由表身份冲突，需要核对控制面结果", rule=route, evidence={"returned": parent_mismatch, "expectedCsnId": csn.get("csnId"), "expectedCsnRtId": table.get("csnRtId")})
                        )
                    if route_type == "propagated":
                        from_attach = str(route.get("fromAttachId") or "")
                        if not from_attach:
                            findings.append(
                                _finding("CSNRULE-006", "high", csn, table, "传播路由缺少 fromAttachId", "无法识别路由学习来源", rule=route, evidence={"routeType": route_type})
                            )
                        elif table.get("_propagationsStatus") == "success" and from_attach not in propagated_in_table:
                            findings.append(
                                _finding("CSNRULE-006", "medium", csn, table, "传播路由来源未出现在该表当前学习关系中", "可能是孤立引用、残留路由或查询期间发生变化", rule=route, evidence={"fromAttachId": from_attach})
                            )
                    elif route_type == "custom" and not _optional_string(route.get("nextHopId")):
                        findings.append(
                            _finding("CSNRULE-007", "medium", csn, table, "自定义路由缺少 nextHopId", "返回的转发目标不完整", rule=route, evidence={"routeType": route_type, "destAddress": destination})
                        )
                    if route_type not in ROUTE_TYPES:
                        findings.append(
                            _finding("CSNRULE-008", "info", csn, table, f"路由类型为 {route_type or 'missing'}", "类型缺失或不在当前文档示例中，需要人工解释", rule=route, evidence={"routeType": route_type or None})
                        )
                for route_id, count in rule_ids.items():
                    if route_id and count > 1:
                        sample = next(route for route in rules if str(route.get("ruleId") or "") == route_id)
                        findings.append(
                            _finding("CSNRULE-003", "high", csn, table, "同一路由表重复返回相同 ruleId", "路由身份重复，需要核对列表或分页数据", rule=sample, evidence={"ruleId": route_id, "occurrences": count})
                        )

        for attach_id, route_table_ids in associated_tables.items():
            valid_ids = sorted(item for item in route_table_ids if item)
            if len(valid_ids) > 1:
                findings.append(
                    _finding("CSNREL-003", "medium", csn, None, "同一 attachId 出现在多张路由表的关联关系中", "网络实例的转发表选择需要人工核对", relationship={"attachId": attach_id}, evidence={"attachId": attach_id, "csnRtIds": valid_ids})
                )

        if csn.get("_instancesStatus") == "success" and all_propagation_queries_success:
            for instance in instances:
                attach_id = str(instance.get("attachId") or "")
                if attach_id and attach_id not in propagated_attachments_all_tables:
                    findings.append(
                        _finding("CSNREL-004", "medium", csn, None, "已加载网络实例未出现在任何学习关系中", "CSN 可能无法从该实例学习路由；也可能是有意隔离", relationship=instance, evidence={"attachId": attach_id, "instanceType": instance.get("instanceType")})
                    )
        if csn.get("_instancesStatus") == "success" and all_association_queries_success:
            for instance in instances:
                attach_id = str(instance.get("attachId") or "")
                if not attach_id or attach_id in associated_attachments_all_tables:
                    continue
                instance_type = str(instance.get("instanceType") or "").lower()
                severity = "high" if instance_type == "channel" else "info"
                interpretation = (
                    "专线通道缺少关联时，CSN 无法向其发布从其他实例学习到的路由"
                    if instance_type == "channel"
                    else "VPC/BEC 可能回退查询默认路由表；仍应核对是否符合隔离设计"
                )
                findings.append(
                    _finding("CSNREL-005", severity, csn, None, "已加载网络实例未出现在任何关联关系中", interpretation, relationship=instance, evidence={"attachId": attach_id, "instanceType": instance_type or None})
                )

    findings.sort(
        key=lambda item: (
            SEVERITY_ORDER.get(str(item.get("severity")), 9),
            str(item.get("ruleId") or ""),
            str(item.get("csnId") or ""),
            str(item.get("csnRtId") or ""),
            str(item.get("routeRuleId") or item.get("attachId") or ""),
        )
    )
    analysis = {
        "summary": {
            "csnCount": len(csns),
            "networkInstanceCount": total_instances,
            "routeTableCount": total_tables,
            "associationCount": total_associations,
            "propagationCount": total_propagations,
            "routeRuleCount": total_rules,
            "findingCount": len(findings),
            "severityCounts": dict(Counter(item["severity"] for item in findings)),
        },
        "distributions": {
            "routeTableType": dict(sorted(route_table_types.items())),
            "associationStatus": dict(sorted(association_statuses.items())),
            "propagationStatus": dict(sorted(propagation_statuses.items())),
            "routeStatus": dict(sorted(route_statuses.items())),
            "routeType": dict(sorted(route_types.items())),
            "nextHopRegion": dict(sorted(route_regions.items())),
        },
        "findings": findings,
    }
    inventory["analysis"] = analysis
    return analysis


def _display(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(inventory: dict[str, Any], analysis: dict[str, Any]) -> str:
    summary = analysis["summary"]
    lines = [
        "# 百度智能云 CSN 路由关联与传播配置排查报告",
        "",
        f"- 生成时间（UTC）：{_display(inventory.get('generatedAt'))}",
        f"- 模式：{_display(inventory.get('mode'))}",
        f"- CSN：{summary['csnCount']}；网络实例：{summary['networkInstanceCount']}；路由表：{summary['routeTableCount']}",
        f"- 关联关系：{summary['associationCount']}；学习关系：{summary['propagationCount']}；路由条目：{summary['routeRuleCount']}",
        f"- 发现数：{summary['findingCount']}",
        "",
        "## 查询覆盖率",
        "",
        "| 范围 | 状态 | 成功范围 | 失败/跳过/阻塞 | 请求数 | 记录数 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    coverage = inventory.get("coverage", {})
    list_cov = coverage.get("listCsns", {})
    lines.append(
        f"| CSN 列表 | {_display(list_cov.get('status'))} | - | {_display(list_cov.get('failedQueries', 0))} | {_display(list_cov.get('queries', 0))} | {_display(list_cov.get('count', 0))} |"
    )
    for label, key, success_key, failed_key, record_key in (
        ("网络实例列表", "listInstances", "successfulCsns", "failedCsns", "instanceCount"),
        ("路由表列表", "listRouteTables", "successfulCsns", "failedCsns", "routeTableCount"),
        ("关联关系", "listAssociations", "successfulRouteTables", "failedRouteTables", "associationCount"),
        ("学习关系", "listPropagations", "successfulRouteTables", "failedRouteTables", "propagationCount"),
        ("路由条目", "listRules", "successfulRouteTables", "failedRouteTables", "routeRuleCount"),
    ):
        item = coverage.get(key, {})
        incomplete = sum(int(item.get(field, 0) or 0) for field in (failed_key, "skippedRouteTables", "blockedCsns"))
        lines.append(
            f"| {label} | {_display(item.get('status'))} | {_display(item.get(success_key, 0))} | {incomplete} | {_display(item.get('queries', 0))} | {_display(item.get(record_key, 0))} |"
        )

    lines.extend([
        "",
        "## 路由表关系矩阵",
        "",
        "| CSN | 路由表 | 类型 | 关联数/状态 | 学习数/状态 | 路由数/状态 |",
        "|---|---|---|---|---|---|",
    ])
    for csn in inventory.get("csns", []):
        if not isinstance(csn, dict):
            continue
        csn_label = f"{_display(csn.get('name'))} ({_display(csn.get('csnId'))})"
        tables = [item for item in csn.get("routeTables", []) if isinstance(item, dict)]
        if not tables:
            lines.append(f"| {csn_label} | - | - | - | - | {_display(csn.get('_routeTablesStatus'))} |")
        for table in tables:
            table_label = f"{_display(table.get('name'))} ({_display(table.get('csnRtId'))})"
            lines.append(
                f"| {csn_label} | {table_label} | {_display(table.get('type'))} | {len(table.get('associations', []))}/{_display(table.get('_associationsStatus'))} | {len(table.get('propagations', []))}/{_display(table.get('_propagationsStatus'))} | {len(table.get('rules', []))}/{_display(table.get('_rulesStatus'))} |"
            )

    lines.extend(["", "## 路由条目", "", "| CSN | 路由表 | 路由 ID | 类型 | 状态 | 目标网段 | 来源挂载 | 下一跳 | 地域 | 黑洞 |", "|---|---|---|---|---|---|---|---|---|---|"])
    route_rows = 0
    for csn in inventory.get("csns", []):
        if not isinstance(csn, dict):
            continue
        for table in csn.get("routeTables", []):
            if not isinstance(table, dict):
                continue
            for rule in table.get("rules", []):
                if not isinstance(rule, dict):
                    continue
                route_rows += 1
                lines.append(
                    f"| {_display(csn.get('csnId'))} | {_display(table.get('csnRtId'))} | {_display(rule.get('ruleId'))} | {_display(rule.get('routeType'))} | {_display(rule.get('status'))} | {_display(rule.get('destAddress'))} | {_display(rule.get('fromAttachId'))} | {_display(rule.get('nextHopId'))} | {_display(rule.get('nextHopRegion'))} | {_display(rule.get('blackHole'))} |"
                )
    if route_rows == 0:
        lines.append("| - | - | - | - | - | - | - | - | - | - |")

    lines.extend(["", "## 分布", ""])
    for label, key in (
        ("路由表类型", "routeTableType"), ("关联状态", "associationStatus"),
        ("学习状态", "propagationStatus"), ("路由状态", "routeStatus"),
        ("路由类型", "routeType"), ("下一跳地域", "nextHopRegion"),
    ):
        values = analysis["distributions"].get(key, {})
        lines.append(f"- {label}：" + ("，".join(f"{_display(name)}={count}" for name, count in values.items()) or "无"))

    lines.extend(["", "## 发现", ""])
    if not analysis["findings"]:
        lines.append("在成功查询且规则覆盖的控制面范围内未发现命中。此结论不代表数据面互通或不存在其他风险。")
    else:
        for finding in analysis["findings"]:
            location = "/".join(
                filter(None, (
                    _optional_string(finding.get("csnId")),
                    _optional_string(finding.get("csnRtId")),
                    _optional_string(finding.get("routeRuleId") or finding.get("attachId")),
                ))
            ) or "全局"
            lines.extend([
                f"### [{finding['severity'].upper()}] {finding['ruleId']} · {location}", "",
                f"- 事实：{finding['fact']}",
                f"- 解释：{finding['interpretation']}",
                f"- 证据：`{json.dumps(finding.get('evidence', {}), ensure_ascii=False, sort_keys=True)}`",
                "",
            ])
    lines.extend([
        "## 限制", "",
        "- 本报告只读取 CSN、网络实例、路由表、关联、学习关系和 CSN 路由条目控制面。",
        "- 未检查 VPC 内路由表、TGW 绑定、路由策略、带宽包、地域带宽、安全组、ACL、专线 CPE 或 BGP 最优路径。",
        "- 路由表之间的隔离、缺失关系和黑洞路由可能是设计意图；变更前必须由网络负责人确认。",
        "- 查询失败范围保持未知，不能按空配置解释；控制面 active 也不能证明数据面可达。", "",
    ])
    return "\n".join(lines)


def _validate_output_dir(path: Path) -> Path:
    skill_root = Path(__file__).resolve().parents[1]
    resolved = path.expanduser().resolve()
    if _is_within(resolved, skill_root):
        raise ValueError("Output directory must be outside the Skill directory")
    return resolved


def _atomic_write(path: Path, data: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_path.exists():
            temporary_path.unlink()


def write_outputs(output_dir: Path, inventory: dict[str, Any], report: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(output_dir, 0o700)
    except OSError:
        pass
    _atomic_write(output_dir / "inventory.json", json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(output_dir / "report.md", report)


def self_test() -> None:
    assert canonical_query({"maxKeys": 1000, "marker": "a b"}) == "marker=a%20b&maxKeys=1000"
    headers = bce_headers("ak", "sk", "/v1/csn", {"maxKeys": 1000}, timestamp="2026-01-01T00:00:00Z")
    assert headers["Authorization"].startswith("bce-auth-v1/ak/")
    client = ReadOnlyBceClient("ak", "sk", max_retries=0)
    try:
        client.request_json("/v1/csn", method="POST")
        raise AssertionError("non-GET request was not rejected")
    except ValueError as exc:
        assert "non-GET" in str(exc)
    sample = {
        "schemaVersion": SCHEMA_VERSION, "generatedAt": utc_now(), "mode": "offline",
        "selection": {"requestedCsnIds": [], "unmatchedCsnIds": []}, "errors": [],
        "csns": [{
            "csnId": "csn-a", "name": "demo", "_instancesStatus": "success",
            "_routeTablesStatus": "success", "instances": [],
            "routeTables": [{
                "csnRtId": "rt-a", "name": "default", "type": "default",
                "_associationsStatus": "success", "_propagationsStatus": "success",
                "_rulesStatus": "success", "associations": [], "propagations": [],
                "rules": [{"ruleId": "rule-a", "routeType": "custom", "csnId": "csn-a", "csnRtId": "rt-a", "status": "conflicted", "destAddress": "10.0.0.0/8", "nextHopId": "vpc-a", "blackHole": True}],
            }],
        }],
    }
    rules = {item["ruleId"] for item in analyze_inventory(sample)["findings"]}
    assert "CSNRULE-001" in rules and "CSNRULE-002" in rules
    assert "CSNRT-003" not in rules
    print("self-test: ok")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only Baidu AI Cloud CSN route-relationship audit")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--input", type=Path, help="Offline inventory JSON")
    mode.add_argument("--self-test", action="store_true", help="Run local tests without cloud access")
    parser.add_argument("--credentials-file", type=Path, help="Owner-only JSON credential file outside the Skill")
    parser.add_argument("--csn-ids", help="Comma-separated exact CSN IDs; live mode only")
    parser.add_argument("--output-dir", type=Path, help="Output directory outside the Skill")
    parser.add_argument("--timeout", type=float, default=20.0, help="Per-request timeout in seconds")
    parser.add_argument("--max-retries", type=int, default=3, help="Retries for GET 429/5xx/network errors")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        if not args.output_dir:
            parser.error("--output-dir is required except with --self-test")
        if args.input and (args.credentials_file or args.csn_ids):
            parser.error("--credentials-file and --csn-ids are live-mode options")
        if args.timeout <= 0 or args.max_retries < 0 or args.max_retries > 10:
            parser.error("--timeout must be positive and --max-retries must be between 0 and 10")
        output_dir = _validate_output_dir(args.output_dir)
        inventory = load_inventory(args.input) if args.input else collect_live(args)
        analysis = analyze_inventory(inventory)
        write_outputs(output_dir, inventory, render_report(inventory, analysis))
        summary = analysis["summary"]
        print(
            "audit complete: "
            f"csns={summary['csnCount']} tables={summary['routeTableCount']} "
            f"associations={summary['associationCount']} propagations={summary['propagationCount']} "
            f"rules={summary['routeRuleCount']} findings={summary['findingCount']}"
        )
        return 0
    except (OSError, ValueError, ApiFailure, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
