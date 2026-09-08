#!/usr/bin/env python3
"""Read-only Baidu AI Cloud VPC peering connectivity configuration diagnosis."""

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
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable


SCHEMA_VERSION = "1.0"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
KNOWN_ROLES = {"initiator", "acceptor"}
TERMINAL_BAD_STATUSES = {"down", "error", "expired", "consult_failed"}
RESOURCE_KEYS = ("vpc", "subnets", "routeTables", "enis", "securityGroups", "acls")


class ApiFailure(RuntimeError):
    """Sanitized API failure without request headers or authorization material."""

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

    def to_dict(self, component: str, scope: str | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {
            "component": component,
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
        ("GET", canonical_uri, canonical_query(params), canonical_headers)
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
        "User-Agent": "baiducloud-peer-connectivity-diagnosis/1.0",
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
        from urllib.parse import urlparse

        endpoint = endpoint.rstrip("/")
        parsed = urlparse(endpoint)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("Endpoint must use HTTPS")
        if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ValueError("Endpoint must be an HTTPS origin without path, query, or fragment")
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
                    str(detail.get("message") or f"HTTP {exc.code}"),
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
        result: list[dict[str, Any]] = []
        while True:
            if marker:
                query["marker"] = marker
            response = self.request_json(path, query)
            result.extend(
                item for item in _first_list(response, item_fields) if isinstance(item, dict)
            )
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
        return result


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


def _resource_id(record: dict[str, Any], *fields: str) -> str | None:
    for field in fields:
        value = _optional_string(record.get(field))
        if value:
            return value
    return None


def _peer_id(record: dict[str, Any]) -> str | None:
    return _resource_id(record, "peerConnId", "id")


def _opposite_role(role: Any) -> str | None:
    normalized = str(role or "").lower()
    if normalized == "initiator":
        return "acceptor"
    if normalized == "acceptor":
        return "initiator"
    return None


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


def _parse_regions(value: str | None) -> list[str]:
    if not value:
        raise ValueError("--regions is required in live mode")
    result: list[str] = []
    for item in value.split(","):
        region = item.strip().lower()
        if not region:
            continue
        if not all(character.isalnum() or character == "-" for character in region):
            raise ValueError(f"Invalid region code: {region}")
        if region not in result:
            result.append(region)
    if not result:
        raise ValueError("At least one region is required")
    return result


def _parse_endpoints(values: list[str]) -> dict[str, str]:
    from urllib.parse import urlparse

    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--endpoint must use REGION=https://host")
        region, endpoint = value.split("=", 1)
        region = region.strip().lower()
        endpoint = endpoint.strip().rstrip("/")
        parsed = urlparse(endpoint)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("Endpoint overrides must use HTTPS")
        if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ValueError("Endpoint overrides must be origins without path, query, or fragment")
        if not parsed.hostname.endswith(".baidubce.com"):
            raise ValueError("Endpoint overrides must use an official *.baidubce.com host")
        result[region] = endpoint
    return result


def _new_endpoint(region: str, vpc_id: str, interface_id: str | None) -> dict[str, Any]:
    return {
        "region": region,
        "vpcId": vpc_id,
        "interfaceId": interface_id,
        "resources": {
            "vpc": None,
            "subnets": [],
            "routeTables": [],
            "enis": [],
            "securityGroups": [],
            "acls": [],
        },
        "coverage": {
            key: {"status": "notAttempted", "count": 0, "queries": 0, "failedQueries": 0}
            for key in RESOURCE_KEYS
        },
        "errors": [],
    }


def _record_endpoint_query(
    endpoint_data: dict[str, Any],
    component: str,
    query: Callable[[], Any],
) -> Any:
    coverage = endpoint_data["coverage"][component]
    coverage["queries"] += 1
    try:
        value = query()
        endpoint_data["resources"][component] = value
        count = len(value) if isinstance(value, list) else int(value is not None)
        coverage.update({"status": "success", "count": count})
        return value
    except ApiFailure as exc:
        coverage.update({"status": "failed", "failedQueries": 1})
        endpoint_data["errors"].append(
            exc.to_dict(component, str(endpoint_data.get("vpcId") or ""))
        )
        return None


def _normalize_route_response(response: dict[str, Any], vpc_id: str) -> list[dict[str, Any]]:
    tables = _first_list(response, ("routeTables",))
    if tables:
        result = []
        for table in tables:
            if isinstance(table, dict):
                item = dict(table)
                item.setdefault("vpcId", vpc_id)
                result.append(item)
        return result
    if response:
        item = dict(response)
        item.setdefault("vpcId", vpc_id)
        return [item]
    return []


def _normalize_acl_response(response: dict[str, Any], vpc_id: str) -> list[dict[str, Any]]:
    entries = _first_list(response, ("aclEntrys", "aclEntries", "acls"))
    result = []
    for entry in entries:
        if isinstance(entry, dict):
            item = dict(entry)
            item.setdefault("vpcId", response.get("vpcId") or vpc_id)
            result.append(item)
    return result


def collect_endpoint(
    client: ReadOnlyBceClient,
    region: str,
    vpc_id: str,
    interface_id: str | None,
    *,
    stop_after_inaccessible_vpc: bool,
) -> dict[str, Any]:
    data = _new_endpoint(region, vpc_id, interface_id)

    def get_vpc() -> dict[str, Any]:
        response = client.request_json(f"/v1/vpc/{_quote(vpc_id)}")
        value = response.get("vpc")
        if isinstance(value, dict):
            return value
        return response

    _record_endpoint_query(data, "vpc", get_vpc)
    vpc_error = data["errors"][-1] if data["errors"] else None
    if (
        stop_after_inaccessible_vpc
        and vpc_error
        and vpc_error.get("component") == "vpc"
        and vpc_error.get("status") in (401, 403, 404)
    ):
        for key in RESOURCE_KEYS:
            if key == "vpc":
                continue
            data["coverage"][key]["status"] = "blocked"
            data["coverage"][key]["reason"] = "Peer VPC is not accessible with this credential"
        return data

    _record_endpoint_query(
        data,
        "subnets",
        lambda: client.paginate("/v1/subnet", ("subnets",), {"vpcId": vpc_id}),
    )
    _record_endpoint_query(
        data,
        "routeTables",
        lambda: _normalize_route_response(
            client.request_json("/v1/route", {"vpcId": vpc_id}), vpc_id
        ),
    )
    _record_endpoint_query(
        data,
        "enis",
        lambda: client.paginate("/v1/eni", ("enis",), {"vpcId": vpc_id}),
    )
    _record_endpoint_query(
        data,
        "securityGroups",
        lambda: client.paginate(
            "/v2/securityGroup", ("securityGroups",), {"vpcId": vpc_id}
        ),
    )
    _record_endpoint_query(
        data,
        "acls",
        lambda: _normalize_acl_response(
            client.request_json("/v1/acl", {"vpcId": vpc_id}), vpc_id
        ),
    )
    return data


def collect_live(args: argparse.Namespace, flow: dict[str, Any]) -> dict[str, Any]:
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
    endpoint_overrides = _parse_endpoints(args.endpoint or [])
    clients: dict[str, ReadOnlyBceClient] = {}

    def client_for(region: str) -> ReadOnlyBceClient:
        normalized = region.lower()
        if normalized not in clients:
            endpoint = endpoint_overrides.get(
                normalized, f"https://bcc.{normalized}.baidubce.com"
            )
            clients[normalized] = ReadOnlyBceClient(
                endpoint,
                access_key,
                secret_key,
                session_token,
                timeout=args.timeout,
                max_retries=args.max_retries,
            )
        return clients[normalized]

    snapshot: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": utc_now(),
        "mode": "live",
        "flow": flow,
        "discoveryRegions": {},
        "diagnoses": [],
    }
    selected: list[tuple[str, dict[str, Any]]] = []

    for region in regions:
        discovery = {
            "coverage": {
                "status": "notAttempted",
                "count": 0,
                "queries": 1,
                "failedQueries": 0,
            },
            "peerConnections": [],
            "errors": [],
        }
        snapshot["discoveryRegions"][region] = discovery
        try:
            summaries = client_for(region).paginate("/v1/peerconn", ("peerConns",))
            discovery["coverage"].update({"status": "success", "count": len(summaries)})
            discovery["peerConnections"] = summaries
        except ApiFailure as exc:
            discovery["coverage"].update({"status": "failed", "failedQueries": 1})
            discovery["errors"].append(exc.to_dict("peerConnections", region))
            continue

        for summary in summaries:
            if args.peer_conn_id and _peer_id(summary) != args.peer_conn_id:
                continue
            peer_conn_id = _peer_id(summary)
            if not peer_conn_id:
                selected.append((region, dict(summary)))
                continue
            params = None
            role = str(summary.get("role") or "").lower()
            if role in KNOWN_ROLES:
                params = {"role": role}
            try:
                detail = client_for(region).request_json(
                    f"/v1/peerconn/{_quote(peer_conn_id)}", params
                )
                merged = dict(summary)
                merged.update(detail)
                merged.setdefault("peerConnId", peer_conn_id)
                merged["_detailStatus"] = "success"
                selected.append((region, merged))
            except ApiFailure as exc:
                merged = dict(summary)
                merged["_detailStatus"] = "failed"
                merged["_detailError"] = exc.to_dict("peerConnectionDetail", peer_conn_id)
                selected.append((region, merged))

    if args.peer_conn_id and not selected:
        successful_regions = [
            region
            for region, data in snapshot["discoveryRegions"].items()
            if data.get("coverage", {}).get("status") == "success"
        ]
        if successful_regions:
            raise ValueError(
                f"Requested peer connection was not returned in regions: {', '.join(successful_regions)}"
            )

    for discovery_region, peer in selected:
        peer_conn_id = _peer_id(peer)
        local_region = str(peer.get("localRegion") or discovery_region).lower()
        local_vpc_id = _optional_string(peer.get("localVpcId"))
        local_interface = _optional_string(peer.get("localIfId"))
        peer_region = str(peer.get("peerRegion") or "").lower()
        peer_vpc_id = _optional_string(peer.get("peerVpcId"))
        diagnosis: dict[str, Any] = {
            "peerConnection": peer,
            "remoteOrientation": {
                "status": "notAttempted",
                "expectedVpcId": peer_vpc_id,
                "returnedVpcId": None,
            },
            "orientationErrors": [],
            "endpoints": {},
        }

        if local_vpc_id:
            diagnosis["endpoints"]["local"] = collect_endpoint(
                client_for(local_region),
                local_region,
                local_vpc_id,
                local_interface,
                stop_after_inaccessible_vpc=False,
            )
        else:
            diagnosis["endpoints"]["local"] = _new_endpoint(
                local_region, "missing", local_interface
            )
            for key in RESOURCE_KEYS:
                diagnosis["endpoints"]["local"]["coverage"][key]["status"] = "blocked"
                diagnosis["endpoints"]["local"]["coverage"][key]["reason"] = (
                    "Connection detail did not return localVpcId"
                )

        remote_detail: dict[str, Any] | None = None
        opposite_role = _opposite_role(peer.get("role"))
        if peer_conn_id and peer_region and peer_vpc_id and opposite_role:
            try:
                remote_detail = client_for(peer_region).request_json(
                    f"/v1/peerconn/{_quote(peer_conn_id)}", {"role": opposite_role}
                )
                returned_vpc_id = _optional_string(remote_detail.get("localVpcId"))
                diagnosis["remoteOrientation"].update(
                    {
                        "status": "success",
                        "returnedVpcId": returned_vpc_id,
                        "role": remote_detail.get("role"),
                    }
                )
            except ApiFailure as exc:
                diagnosis["remoteOrientation"]["status"] = "failed"
                diagnosis["orientationErrors"].append(
                    exc.to_dict("remotePeerConnectionDetail", peer_conn_id)
                )
        else:
            diagnosis["remoteOrientation"]["status"] = "blocked"
            diagnosis["remoteOrientation"]["reason"] = (
                "Peer region, VPC ID, connection ID, or documented role is missing"
            )

        if peer_region and peer_vpc_id:
            remote_interface = None
            if (
                remote_detail
                and _optional_string(remote_detail.get("localVpcId")) == peer_vpc_id
            ):
                remote_interface = _optional_string(remote_detail.get("localIfId"))
            diagnosis["endpoints"]["peer"] = collect_endpoint(
                client_for(peer_region),
                peer_region,
                peer_vpc_id,
                remote_interface,
                stop_after_inaccessible_vpc=True,
            )
        else:
            diagnosis["endpoints"]["peer"] = _new_endpoint(
                peer_region or "missing", peer_vpc_id or "missing", None
            )
            for key in RESOURCE_KEYS:
                diagnosis["endpoints"]["peer"]["coverage"][key]["status"] = "blocked"
                diagnosis["endpoints"]["peer"]["coverage"][key]["reason"] = (
                    "Connection detail did not return peer region or peer VPC ID"
                )
        snapshot["diagnoses"].append(diagnosis)

    return snapshot


def load_snapshot(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        snapshot = json.load(handle)
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("diagnoses"), list):
        raise ValueError("Snapshot must be a JSON object containing a diagnoses list")
    snapshot.setdefault("schemaVersion", SCHEMA_VERSION)
    snapshot.setdefault("generatedAt", utc_now())
    snapshot["mode"] = "offline"
    snapshot.setdefault("flow", {})
    snapshot.setdefault("discoveryRegions", {})
    for diagnosis in snapshot["diagnoses"]:
        if not isinstance(diagnosis, dict):
            raise ValueError("Every diagnosis must be a JSON object")
        diagnosis.setdefault("peerConnection", {})
        diagnosis.setdefault("remoteOrientation", {"status": "unknown"})
        diagnosis.setdefault("orientationErrors", [])
        endpoints = diagnosis.setdefault("endpoints", {})
        for side in ("local", "peer"):
            endpoint = endpoints.setdefault(side, {})
            resources = endpoint.setdefault("resources", {})
            coverage = endpoint.setdefault("coverage", {})
            endpoint.setdefault("errors", [])
            for key in RESOURCE_KEYS:
                default_value: Any = None if key == "vpc" else []
                resources.setdefault(key, default_value)
                value = resources[key]
                count = len(value) if isinstance(value, list) else int(value is not None)
                coverage.setdefault(key, {"status": "unknown", "count": count})
    return snapshot


def _finding(
    rule_id: str,
    severity: str,
    confidence: str,
    peer: dict[str, Any],
    side: str,
    fact: str,
    interpretation: str,
    *,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ruleId": rule_id,
        "severity": severity,
        "confidence": confidence,
        "peerConnId": _peer_id(peer),
        "side": side,
        "fact": fact,
        "interpretation": interpretation,
        "evidence": evidence or {},
    }


def _as_network(value: Any) -> ipaddress.IPv4Network | ipaddress.IPv6Network | None:
    text = str(value or "").strip().lower()
    if text in {"all", "any"}:
        text = "0.0.0.0/0"
    try:
        return ipaddress.ip_network(text, strict=False)
    except ValueError:
        return None


def _address_matches_ip(value: Any, address: ipaddress._BaseAddress) -> bool | None:
    text = str(value or "").strip().lower()
    if text in {"all", "any"}:
        return True
    network = _as_network(value)
    if network is None:
        return None
    if network.version != address.version:
        return False
    return address in network


def _network_covers_network(value: Any, target: Any) -> bool | None:
    first = _as_network(value)
    second = _as_network(target)
    if first is None or second is None:
        return None
    if first.version != second.version:
        return False
    return first == second or first.supernet_of(second)


def _find_subnets(endpoint: dict[str, Any], address: ipaddress._BaseAddress) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for subnet in endpoint.get("resources", {}).get("subnets", []):
        if not isinstance(subnet, dict):
            continue
        for field in ("cidr", "ipv6Cidr"):
            network = _as_network(subnet.get(field))
            if network and network.version == address.version and address in network:
                result.append(subnet)
                break
    return result


def _route_rules(endpoint: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for table in endpoint.get("resources", {}).get("routeTables", []):
        if not isinstance(table, dict):
            continue
        rules = table.get("routeRules")
        if not isinstance(rules, list):
            continue
        for rule in rules:
            if isinstance(rule, dict):
                item = dict(rule)
                item.setdefault("routeTableId", table.get("routeTableId"))
                result.append(item)
    return result


def _route_hops(rule: dict[str, Any]) -> list[tuple[str, str | None]]:
    result: list[tuple[str, str | None]] = []
    hop_type = str(rule.get("nexthopType") or "")
    hop_id = _optional_string(rule.get("nexthopId"))
    if hop_type or hop_id:
        result.append((hop_type, hop_id))
    values = rule.get("nextHopList")
    if isinstance(values, list):
        for item in values:
            if isinstance(item, dict):
                result.append(
                    (
                        str(item.get("nexthopType") or ""),
                        _optional_string(item.get("nexthopId")),
                    )
                )
    return result


def _is_peer_hop(hop_type: str) -> bool:
    return hop_type.strip().lower() == "peerconn"


def _route_has_expected_peer(rule: dict[str, Any], interface_id: str) -> bool:
    return any(
        _is_peer_hop(hop_type) and hop_id == interface_id
        for hop_type, hop_id in _route_hops(rule)
    )


def _route_has_other_peer(rule: dict[str, Any], interface_id: str) -> bool:
    return any(
        _is_peer_hop(hop_type) and hop_id != interface_id
        for hop_type, hop_id in _route_hops(rule)
    )


def _route_matches_flow(
    rule: dict[str, Any],
    source: ipaddress._BaseAddress,
    destination: ipaddress._BaseAddress,
) -> bool | None:
    source_match = _address_matches_ip(rule.get("sourceAddress"), source)
    destination_match = _address_matches_ip(rule.get("destinationAddress"), destination)
    if source_match is False or destination_match is False:
        return False
    if source_match is None or destination_match is None:
        return None
    return True


def _route_evidence(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        key: rule.get(key)
        for key in (
            "routeRuleId",
            "routeTableId",
            "sourceAddress",
            "destinationAddress",
            "nexthopType",
            "nexthopId",
            "nextHopList",
        )
        if rule.get(key) is not None
    }


def _analyze_precise_routes(
    peer: dict[str, Any],
    endpoint: dict[str, Any],
    side: str,
    source: ipaddress._BaseAddress,
    destination: ipaddress._BaseAddress,
    missing_rule_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    coverage = endpoint.get("coverage", {}).get("routeTables", {}).get("status")
    interface_id = _optional_string(endpoint.get("interfaceId"))
    result: dict[str, Any] = {
        "side": side,
        "routeCoverage": coverage,
        "interfaceId": interface_id,
        "matchingPeerRouteIds": [],
        "matchingOtherRouteIds": [],
        "verdict": "unknown",
    }
    if coverage != "success" or not interface_id:
        findings.append(
            _finding(
                "ROUTE-006",
                "info",
                "unknown",
                peer,
                side,
                "无法完成精确下一跳校验",
                "路由查询或该端 localIfId 不完整",
                evidence={"routeCoverage": coverage, "interfaceId": interface_id},
            )
        )
        return findings, result

    matching: list[dict[str, Any]] = []
    unparseable = False
    for rule in _route_rules(endpoint):
        matched = _route_matches_flow(rule, source, destination)
        if matched is True:
            matching.append(rule)
        elif matched is None:
            unparseable = True
    expected = [rule for rule in matching if _route_has_expected_peer(rule, interface_id)]
    wrong_peer = [rule for rule in matching if _route_has_other_peer(rule, interface_id)]
    other = [rule for rule in matching if not _route_has_expected_peer(rule, interface_id)]
    result["matchingPeerRouteIds"] = [
        _resource_id(rule, "routeRuleId") for rule in expected
    ]
    result["matchingOtherRouteIds"] = [
        _resource_id(rule, "routeRuleId") for rule in other
    ]

    if not expected:
        result["verdict"] = "missing"
        findings.append(
            _finding(
                missing_rule_id,
                "high",
                "candidate" if unparseable else "confirmed",
                peer,
                side,
                "未找到覆盖本次流量且指向正确本端接口的对等连接路由",
                "该方向缺少可验证的对等连接路由，是连通性阻断候选",
                evidence={
                    "sourceIp": str(source),
                    "destinationIp": str(destination),
                    "expectedInterfaceId": interface_id,
                    "matchingRoutes": [_route_evidence(rule) for rule in matching],
                    "unparseableRoutePresent": unparseable,
                },
            )
        )
    else:
        result["verdict"] = "matched"

    if wrong_peer:
        findings.append(
            _finding(
                "ROUTE-005",
                "medium",
                "confirmed",
                peer,
                side,
                "匹配流量的 peerConn 路由引用了其他下一跳 ID",
                "对等连接路由应引用该端 localIfId，而不是连接 ID 或其他接口",
                evidence={
                    "expectedInterfaceId": interface_id,
                    "wrongRoutes": [_route_evidence(rule) for rule in wrong_peer],
                },
            )
        )

    if expected:
        expected_prefixes = [
            network.prefixlen
            for rule in expected
            if (network := _as_network(rule.get("destinationAddress"))) is not None
        ]
        if expected_prefixes:
            best_peer_prefix = max(expected_prefixes)
            competitors = []
            for rule in other:
                network = _as_network(rule.get("destinationAddress"))
                if network and network.prefixlen > best_peer_prefix:
                    competitors.append(rule)
            if competitors:
                findings.append(
                    _finding(
                        "ROUTE-004",
                        "high",
                        "candidate",
                        peer,
                        side,
                        "存在比对等连接路由目标网段更具体的其他匹配路由",
                        "最长前缀可能把流量导向其他下一跳",
                        evidence={
                            "peerDestinationPrefix": best_peer_prefix,
                            "competingRoutes": [
                                _route_evidence(rule) for rule in competitors
                            ],
                        },
                    )
                )
    return findings, result


def _topology_route_gaps(
    peer: dict[str, Any],
    endpoint: dict[str, Any],
    opposite_endpoint: dict[str, Any],
    side: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    coverage = endpoint.get("coverage", {}).get("routeTables", {}).get("status")
    opposite_coverage = opposite_endpoint.get("coverage", {}).get("subnets", {}).get("status")
    interface_id = _optional_string(endpoint.get("interfaceId"))
    if coverage != "success" or opposite_coverage != "success" or not interface_id:
        findings.append(
            _finding(
                "ROUTE-006",
                "info",
                "unknown",
                peer,
                side,
                "无法完成对端子网的路由覆盖检查",
                "路由、对端子网或本端接口 ID 证据不完整",
                evidence={
                    "routeCoverage": coverage,
                    "oppositeSubnetCoverage": opposite_coverage,
                    "interfaceId": interface_id,
                },
            )
        )
        return findings

    routes = _route_rules(endpoint)
    for subnet in opposite_endpoint.get("resources", {}).get("subnets", []):
        if not isinstance(subnet, dict):
            continue
        cidrs = [subnet.get("cidr"), subnet.get("ipv6Cidr")]
        for cidr in [value for value in cidrs if value]:
            matched = any(
                _network_covers_network(rule.get("destinationAddress"), cidr) is True
                and _route_has_expected_peer(rule, interface_id)
                for rule in routes
            )
            if not matched:
                findings.append(
                    _finding(
                        "ROUTE-003",
                        "medium",
                        "candidate",
                        peer,
                        side,
                        f"未找到覆盖对端子网 {cidr} 且指向预期接口的路由",
                        "该子网可能不在此对等连接的可达范围内；需结合源网段规则复核",
                        evidence={
                            "oppositeSubnetId": _resource_id(subnet, "subnetId", "id"),
                            "oppositeSubnetCidr": cidr,
                            "expectedInterfaceId": interface_id,
                        },
                    )
                )
    return findings


def _eni_addresses(eni: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for field in ("privateIpAddress", "primaryPrivateIpAddress", "ipAddress"):
        value = _optional_string(eni.get(field))
        if value:
            result.add(value)
    for field in ("privateIpSet", "privateIps", "privateIpAddresses"):
        values = eni.get(field)
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, dict):
                address = _resource_id(
                    value, "privateIpAddress", "ipAddress", "address"
                )
            else:
                address = _optional_string(value)
            if address:
                result.add(address)
    return result


def _reference_ids(record: dict[str, Any], *fields: str) -> set[str]:
    result: set[str] = set()
    for field in fields:
        value = record.get(field)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    item_id = _resource_id(
                        item,
                        "id",
                        "securityGroupId",
                        "enterpriseSecurityGroupId",
                    )
                else:
                    item_id = _optional_string(item)
                if item_id:
                    result.add(item_id)
        elif isinstance(value, str):
            result.add(value)
    return result


def _protocol_matches(rule_value: Any, protocol: str) -> bool:
    rule_protocol = str(rule_value or "all").strip().lower()
    if rule_protocol in {"", "all", "any", "-1"}:
        return True
    return rule_protocol == protocol.lower()


def _port_matches(value: Any, port: int | None, *, default_all: bool = True) -> bool | None:
    text = str(value or ("1-65535" if default_all else "")).strip().lower().replace(" ", "")
    if text in {"all", "any", "-1", "0-65535", "1-65535"}:
        return True
    if not text:
        return None
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
    if port is None:
        return any(start <= 1 and end >= 65535 for start, end in intervals) or None
    return any(start <= port <= end for start, end in intervals)


def _sg_rule_match(
    rule: dict[str, Any],
    direction: str,
    remote_ip: ipaddress._BaseAddress,
    protocol: str,
    port: int | None,
) -> bool | None:
    if str(rule.get("direction") or "").lower() != direction:
        return False
    if not _protocol_matches(rule.get("protocol"), protocol):
        return False
    if protocol in {"tcp", "udp"}:
        port_match = _port_matches(rule.get("portRange"), port)
        if port_match is not True:
            return port_match
    remote_field = "sourceIp" if direction == "ingress" else "destIp"
    group_field = "sourceGroupId" if direction == "ingress" else "destGroupId"
    if rule.get(group_field) or rule.get("remoteIpSet") or rule.get("remoteIpGroup"):
        return None
    return _address_matches_ip(rule.get(remote_field), remote_ip)


def _analyze_security_group(
    peer: dict[str, Any],
    endpoint: dict[str, Any],
    side: str,
    local_ip: ipaddress._BaseAddress,
    remote_ip: ipaddress._BaseAddress,
    direction: str,
    protocol: str | None,
    port: int | None,
    blocked_rule_id: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not protocol or (protocol in {"tcp", "udp"} and port is None):
        return [
            _finding(
                "SG-003",
                "info",
                "unknown",
                peer,
                side,
                "未提供完整协议/端口，跳过普通安全组精确判断",
                "补充 TCP/UDP 端口或明确 ICMP 后再判断策略",
            )
        ]
    coverage = endpoint.get("coverage", {})
    if (
        coverage.get("enis", {}).get("status") != "success"
        or coverage.get("securityGroups", {}).get("status") != "success"
    ):
        return [
            _finding(
                "SG-003",
                "info",
                "unknown",
                peer,
                side,
                "ENI 或普通安全组查询不完整",
                "不能据此判断安全组允许或阻断",
                evidence={
                    "eniCoverage": coverage.get("enis", {}).get("status"),
                    "securityGroupCoverage": coverage.get("securityGroups", {}).get("status"),
                },
            )
        ]

    enis = [
        eni
        for eni in endpoint.get("resources", {}).get("enis", [])
        if isinstance(eni, dict) and str(local_ip) in _eni_addresses(eni)
    ]
    if not enis:
        return [
            _finding(
                "SG-003",
                "info",
                "unknown",
                peer,
                side,
                f"未将 IP {local_ip} 映射到弹性网卡",
                "无法确定该地址实际关联的安全组",
                evidence={"localIp": str(local_ip)},
            )
        ]

    ordinary_ids: set[str] = set()
    enterprise_ids: set[str] = set()
    for eni in enis:
        ordinary_ids.update(
            _reference_ids(eni, "securityGroupIds", "securityGroups")
        )
        enterprise_ids.update(
            _reference_ids(
                eni,
                "enterpriseSecurityGroupIds",
                "enterpriseSecurityGroups",
            )
        )
    if enterprise_ids:
        findings.append(
            _finding(
                "POLICY-001",
                "info",
                "unknown",
                peer,
                side,
                "ENI 返回企业安全组引用，本 Skill 未解析其最终合并语义",
                "普通安全组结论不能排除企业安全组继续阻断",
                evidence={"enterpriseSecurityGroupIds": sorted(enterprise_ids)},
            )
        )
    if not ordinary_ids:
        findings.append(
            _finding(
                "SG-003",
                "info",
                "unknown",
                peer,
                side,
                "ENI 未返回普通安全组 ID",
                "无法完成普通安全组匹配",
                evidence={
                    "eniIds": [_resource_id(eni, "eniId", "id") for eni in enis]
                },
            )
        )
        return findings

    group_index = {
        group_id: group
        for group in endpoint.get("resources", {}).get("securityGroups", [])
        if isinstance(group, dict)
        and (group_id := _resource_id(group, "id", "securityGroupId"))
    }
    missing_ids = sorted(ordinary_ids - set(group_index))
    if missing_ids:
        findings.append(
            _finding(
                "SG-003",
                "info",
                "unknown",
                peer,
                side,
                "ENI 引用的部分普通安全组未出现在查询结果中",
                "安全组证据不完整，不能形成阻断结论",
                evidence={"missingSecurityGroupIds": missing_ids},
            )
        )
        return findings

    matches: list[dict[str, Any]] = []
    unresolved = False
    for group_id in sorted(ordinary_ids):
        rules = group_index[group_id].get("rules")
        if not isinstance(rules, list):
            unresolved = True
            continue
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            matched = _sg_rule_match(rule, direction, remote_ip, protocol, port)
            if matched is True:
                matches.append(
                    {
                        "securityGroupId": group_id,
                        "securityGroupRuleId": _resource_id(
                            rule, "securityGroupRuleId", "id"
                        ),
                    }
                )
            elif matched is None:
                unresolved = True
    if not matches and not unresolved:
        findings.append(
            _finding(
                blocked_rule_id,
                "high",
                "candidate",
                peer,
                side,
                f"关联普通安全组中没有匹配的 {direction} allow 规则",
                "普通安全组是本次精确流量的阻断候选",
                evidence={
                    "localIp": str(local_ip),
                    "remoteIp": str(remote_ip),
                    "protocol": protocol,
                    "port": port,
                    "securityGroupIds": sorted(ordinary_ids),
                },
            )
        )
    elif unresolved and not matches:
        findings.append(
            _finding(
                "SG-003",
                "info",
                "unknown",
                peer,
                side,
                "安全组含地址组引用或不可解析字段，未找到直接 IP 匹配规则",
                "不能把未匹配直接解释为阻断",
                evidence={"securityGroupIds": sorted(ordinary_ids)},
            )
        )
    return findings


def _acl_rule_match(
    rule: dict[str, Any],
    direction: str,
    source: ipaddress._BaseAddress,
    destination: ipaddress._BaseAddress,
    protocol: str,
    port: int | None,
) -> bool | None:
    if str(rule.get("direction") or "").lower() != direction:
        return False
    if not _protocol_matches(rule.get("protocol"), protocol):
        return False
    source_match = _address_matches_ip(rule.get("sourceIpAddress"), source)
    destination_match = _address_matches_ip(rule.get("destinationIpAddress"), destination)
    if source_match is False or destination_match is False:
        return False
    if source_match is None or destination_match is None:
        return None
    if protocol in {"tcp", "udp"}:
        source_port_match = _port_matches(rule.get("sourcePort"), None)
        destination_port_match = _port_matches(rule.get("destinationPort"), port)
        if source_port_match is False or destination_port_match is False:
            return False
        if source_port_match is None or destination_port_match is None:
            return None
    return True


def _position(rule: dict[str, Any]) -> int | None:
    try:
        return int(rule.get("position"))
    except (TypeError, ValueError):
        return None


def _analyze_acl(
    peer: dict[str, Any],
    endpoint: dict[str, Any],
    side: str,
    subnet: dict[str, Any],
    source: ipaddress._BaseAddress,
    destination: ipaddress._BaseAddress,
    direction: str,
    protocol: str | None,
    port: int | None,
    deny_rule_id: str,
) -> list[dict[str, Any]]:
    if not protocol or (protocol in {"tcp", "udp"} and port is None):
        return [
            _finding(
                "ACL-003",
                "info",
                "unknown",
                peer,
                side,
                "未提供完整协议/端口，跳过 ACL 精确判断",
                "补充协议和目标端口后再按优先级匹配",
            )
        ]
    coverage = endpoint.get("coverage", {}).get("acls", {}).get("status")
    if coverage != "success":
        return [
            _finding(
                "ACL-003",
                "info",
                "unknown",
                peer,
                side,
                "ACL 查询不完整",
                "不能据此判断 ACL 允许或阻断",
                evidence={"aclCoverage": coverage},
            )
        ]
    subnet_id = _resource_id(subnet, "subnetId", "id")
    entries = [
        entry
        for entry in endpoint.get("resources", {}).get("acls", [])
        if isinstance(entry, dict)
        and _resource_id(entry, "subnetId", "id") == subnet_id
    ]
    if not entries:
        return []
    rules: list[dict[str, Any]] = []
    for entry in entries:
        values = entry.get("aclRules")
        if isinstance(values, list):
            rules.extend(rule for rule in values if isinstance(rule, dict))
    if not rules:
        return [
            _finding(
                "ACL-003",
                "info",
                "unknown",
                peer,
                side,
                "子网 ACL 条目未返回可判断的规则",
                "不能推断默认允许或拒绝行为",
                evidence={"subnetId": subnet_id},
            )
        ]
    ordered = sorted(
        (rule for rule in rules if _position(rule) is not None),
        key=lambda rule: _position(rule) or 0,
    )
    unresolved = len(ordered) != len(rules)
    for rule in ordered:
        matched = _acl_rule_match(
            rule, direction, source, destination, protocol, port
        )
        if matched is None:
            unresolved = True
            continue
        if matched is not True:
            continue
        action = str(rule.get("action") or "").lower()
        if action == "deny":
            return [
                _finding(
                    deny_rule_id,
                    "high",
                    "confirmed",
                    peer,
                    side,
                    f"首条匹配的 {direction} ACL 规则显式拒绝流量",
                    "该子网 ACL 是本次正向流量的已确认阻断项",
                    evidence={
                        "subnetId": subnet_id,
                        "aclRuleId": _resource_id(rule, "id", "aclRuleId"),
                        "position": rule.get("position"),
                        "action": action,
                    },
                )
            ]
        if action == "allow":
            return []
        unresolved = True
        break
    return [
        _finding(
            "ACL-003",
            "info",
            "unknown",
            peer,
            side,
            "没有得到可确定的 ACL 首匹配结果",
            "存在不可解析规则或没有匹配规则，不能推断默认动作",
            evidence={"subnetId": subnet_id, "unresolvedRules": unresolved},
        )
    ]


def _coverage_findings(
    peer: dict[str, Any],
    endpoint: dict[str, Any],
    side: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for error in endpoint.get("errors", []):
        status = error.get("status")
        if side == "peer" and status in (401, 403, 404):
            rule_id, severity = "COV-003", "info"
            interpretation = "对端可能属于另一账号；远端配置保持未验证"
        elif status in (401, 403):
            rule_id, severity = "COV-002", "high"
            interpretation = "本端身份或只读权限不足，结论不完整"
        elif status == 404:
            rule_id, severity = "COV-004", "info"
            interpretation = "核对地域、资源 ID 和账号范围"
        else:
            rule_id, severity = "COV-001", "high"
            interpretation = "查询失败导致诊断覆盖不完整"
        findings.append(
            _finding(
                rule_id,
                severity,
                "unknown",
                peer,
                side,
                f"{error.get('component', 'resource')} 查询失败，状态为 {status or 'network-error'}",
                interpretation,
                evidence={
                    key: error.get(key)
                    for key in ("component", "status", "code", "requestId", "path", "scope")
                    if error.get(key) is not None
                },
            )
        )
    return findings


def _subnet_overlap_findings(
    peer: dict[str, Any],
    local: dict[str, Any],
    remote: dict[str, Any],
) -> list[dict[str, Any]]:
    if (
        local.get("coverage", {}).get("subnets", {}).get("status") != "success"
        or remote.get("coverage", {}).get("subnets", {}).get("status") != "success"
    ):
        return []
    overlaps: list[dict[str, Any]] = []
    for local_subnet in local.get("resources", {}).get("subnets", []):
        if not isinstance(local_subnet, dict):
            continue
        for remote_subnet in remote.get("resources", {}).get("subnets", []):
            if not isinstance(remote_subnet, dict):
                continue
            for field in ("cidr", "ipv6Cidr"):
                first = _as_network(local_subnet.get(field))
                second = _as_network(remote_subnet.get(field))
                if first and second and first.version == second.version and first.overlaps(second):
                    overlaps.append(
                        {
                            "localSubnetId": _resource_id(local_subnet, "subnetId", "id"),
                            "localCidr": str(first),
                            "peerSubnetId": _resource_id(remote_subnet, "subnetId", "id"),
                            "peerCidr": str(second),
                        }
                    )
    if not overlaps:
        return []
    return [
        _finding(
            "ADDR-003",
            "info",
            "candidate",
            peer,
            "both",
            f"发现 {len(overlaps)} 对重叠的两端子网 CIDR",
            "VPC 整体 CIDR 可重叠，但实际互通的两端子网不能重叠；需结合目标流量确认",
            evidence={"overlappingSubnetPairs": overlaps[:50]},
        )
    ]


def analyze_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []
    flow = snapshot.get("flow", {}) if isinstance(snapshot.get("flow"), dict) else {}
    source_text = _optional_string(flow.get("sourceIp"))
    destination_text = _optional_string(flow.get("destinationIp"))
    protocol = _optional_string(flow.get("protocol"))
    protocol = protocol.lower() if protocol else None
    port = flow.get("port") if isinstance(flow.get("port"), int) else None
    precise = bool(source_text and destination_text)
    source = ipaddress.ip_address(source_text) if source_text else None
    destination = ipaddress.ip_address(destination_text) if destination_text else None

    for region, discovery in snapshot.get("discoveryRegions", {}).items():
        for error in discovery.get("errors", []):
            status = error.get("status")
            rule_id = "COV-002" if status in (401, 403) else "COV-004" if status == 404 else "COV-001"
            findings.append(
                {
                    "ruleId": rule_id,
                    "severity": "info" if rule_id == "COV-004" else "high",
                    "confidence": "unknown",
                    "peerConnId": None,
                    "side": "discovery",
                    "fact": f"地域 {region} 的对等连接列表查询失败",
                    "interpretation": "该地域没有可诊断的完整连接清单",
                    "evidence": {
                        key: error.get(key)
                        for key in ("status", "code", "requestId", "path")
                        if error.get(key) is not None
                    },
                }
            )

    for diagnosis in snapshot.get("diagnoses", []):
        if not isinstance(diagnosis, dict):
            continue
        peer = diagnosis.get("peerConnection", {})
        endpoints = diagnosis.get("endpoints", {})
        local = endpoints.get("local", {})
        remote = endpoints.get("peer", {})
        path_result: dict[str, Any] = {
            "peerConnId": _peer_id(peer),
            "mode": "precise" if precise else "topology",
            "sourceSubnetId": None,
            "destinationSubnetId": None,
            "forwardRoute": "notEvaluated",
            "reverseRoute": "notEvaluated",
        }

        detail_error = peer.get("_detailError")
        if isinstance(detail_error, dict):
            status = detail_error.get("status")
            findings.append(
                _finding(
                    "COV-002" if status in (401, 403) else "COV-004" if status == 404 else "COV-001",
                    "info" if status == 404 else "high",
                    "unknown",
                    peer,
                    "local",
                    "本端对等连接详情查询失败",
                    "诊断继续使用列表字段，详情专属字段可能缺失",
                    evidence=detail_error,
                )
            )
        findings.extend(_coverage_findings(peer, local, "local"))
        findings.extend(_coverage_findings(peer, remote, "peer"))

        for error in diagnosis.get("orientationErrors", []):
            findings.append(
                _finding(
                    "COV-003",
                    "info",
                    "unknown",
                    peer,
                    "peer",
                    "无法读取对端方向的对等连接详情",
                    "跨账号或权限边界可能使对端接口 ID 无法验证",
                    evidence={
                        key: error.get(key)
                        for key in ("status", "code", "requestId", "path")
                        if error.get(key) is not None
                    },
                )
            )
        orientation = diagnosis.get("remoteOrientation", {})
        if (
            orientation.get("status") == "success"
            and orientation.get("expectedVpcId")
            and orientation.get("returnedVpcId") != orientation.get("expectedVpcId")
        ):
            findings.append(
                _finding(
                    "CONN-003",
                    "high",
                    "confirmed",
                    peer,
                    "peer",
                    "对端详情返回的本端 VPC 与原连接声明的对端 VPC 不一致",
                    "连接方向或 role 选择异常，停止自动推断对端下一跳",
                    evidence=orientation,
                )
            )

        status = str(peer.get("status") or "").lower()
        if status in TERMINAL_BAD_STATUSES:
            findings.append(
                _finding(
                    "CONN-001",
                    "high",
                    "confirmed",
                    peer,
                    "both",
                    f"对等连接状态为 {status}",
                    "连接控制面状态已报告不可用、异常、到期或协商失败",
                    evidence={"status": status},
                )
            )
        elif status != "active":
            findings.append(
                _finding(
                    "CONN-002",
                    "medium",
                    "confirmed" if status else "unknown",
                    peer,
                    "both",
                    f"对等连接状态为 {status or 'missing'}",
                    "连接当前不是 active；过渡状态不等于卡死",
                    evidence={"status": status or None},
                )
            )

        if precise and source is not None and destination is not None:
            local_subnets = (
                _find_subnets(local, source)
                if local.get("coverage", {}).get("subnets", {}).get("status") == "success"
                else []
            )
            remote_subnets = (
                _find_subnets(remote, destination)
                if remote.get("coverage", {}).get("subnets", {}).get("status") == "success"
                else []
            )
            if local.get("coverage", {}).get("subnets", {}).get("status") == "success" and not local_subnets:
                findings.append(
                    _finding(
                        "ADDR-001",
                        "high",
                        "confirmed",
                        peer,
                        "local",
                        f"源 IP {source} 不属于本端成功查询到的任何子网",
                        "源地址与所选对等连接方向不匹配",
                        evidence={"sourceIp": str(source)},
                    )
                )
            if remote.get("coverage", {}).get("subnets", {}).get("status") == "success" and not remote_subnets:
                findings.append(
                    _finding(
                        "ADDR-001",
                        "high",
                        "confirmed",
                        peer,
                        "peer",
                        f"目的 IP {destination} 不属于对端成功查询到的任何子网",
                        "目的地址与所选对等连接方向不匹配",
                        evidence={"destinationIp": str(destination)},
                    )
                )
            source_subnet = max(
                local_subnets,
                key=lambda item: max(
                    [
                        network.prefixlen
                        for field in ("cidr", "ipv6Cidr")
                        if (network := _as_network(item.get(field))) is not None
                    ]
                    or [-1]
                ),
                default=None,
            )
            destination_subnet = max(
                remote_subnets,
                key=lambda item: max(
                    [
                        network.prefixlen
                        for field in ("cidr", "ipv6Cidr")
                        if (network := _as_network(item.get(field))) is not None
                    ]
                    or [-1]
                ),
                default=None,
            )
            path_result["sourceSubnetId"] = (
                _resource_id(source_subnet, "subnetId", "id") if source_subnet else None
            )
            path_result["destinationSubnetId"] = (
                _resource_id(destination_subnet, "subnetId", "id")
                if destination_subnet
                else None
            )
            if source_subnet and destination_subnet:
                source_networks = [
                    network
                    for field in ("cidr", "ipv6Cidr")
                    if (network := _as_network(source_subnet.get(field))) is not None
                ]
                destination_networks = [
                    network
                    for field in ("cidr", "ipv6Cidr")
                    if (network := _as_network(destination_subnet.get(field))) is not None
                ]
                if any(
                    first.version == second.version and first.overlaps(second)
                    for first in source_networks
                    for second in destination_networks
                ):
                    findings.append(
                        _finding(
                            "ADDR-002",
                            "high",
                            "confirmed",
                            peer,
                            "both",
                            "本次流量定位到的两端子网 CIDR 重叠",
                            "官方典型实践要求实际互通的两端子网不重叠",
                            evidence={
                                "sourceSubnetId": path_result["sourceSubnetId"],
                                "destinationSubnetId": path_result["destinationSubnetId"],
                            },
                        )
                    )

            forward_findings, forward_result = _analyze_precise_routes(
                peer, local, "local", source, destination, "ROUTE-001"
            )
            reverse_findings, reverse_result = _analyze_precise_routes(
                peer, remote, "peer", destination, source, "ROUTE-002"
            )
            findings.extend(forward_findings)
            findings.extend(reverse_findings)
            path_result["forwardRoute"] = forward_result.get("verdict")
            path_result["reverseRoute"] = reverse_result.get("verdict")

            findings.extend(
                _analyze_security_group(
                    peer,
                    local,
                    "local",
                    source,
                    destination,
                    "egress",
                    protocol,
                    port,
                    "SG-001",
                )
            )
            findings.extend(
                _analyze_security_group(
                    peer,
                    remote,
                    "peer",
                    destination,
                    source,
                    "ingress",
                    protocol,
                    port,
                    "SG-002",
                )
            )
            if source_subnet:
                findings.extend(
                    _analyze_acl(
                        peer,
                        local,
                        "local",
                        source_subnet,
                        source,
                        destination,
                        "egress",
                        protocol,
                        port,
                        "ACL-001",
                    )
                )
            if destination_subnet:
                findings.extend(
                    _analyze_acl(
                        peer,
                        remote,
                        "peer",
                        destination_subnet,
                        source,
                        destination,
                        "ingress",
                        protocol,
                        port,
                        "ACL-002",
                    )
                )
        else:
            findings.extend(_subnet_overlap_findings(peer, local, remote))
            findings.extend(_topology_route_gaps(peer, local, remote, "local"))
            findings.extend(_topology_route_gaps(peer, remote, local, "peer"))
        paths.append(path_result)

    findings.sort(
        key=lambda item: (
            SEVERITY_ORDER.get(str(item.get("severity")), 9),
            str(item.get("peerConnId") or ""),
            str(item.get("ruleId") or ""),
            str(item.get("side") or ""),
        )
    )
    return {
        "generatedAt": utc_now(),
        "sourceGeneratedAt": snapshot.get("generatedAt"),
        "summary": {
            "diagnosedConnections": len(snapshot.get("diagnoses", [])),
            "mode": "precise" if precise else "topology",
            "pathVerdicts": dict(
                Counter(
                    result.get("forwardRoute", "unknown")
                    for result in paths
                )
            ),
        },
        "findingCounts": {
            severity: sum(1 for item in findings if item.get("severity") == severity)
            for severity in ("high", "medium", "low", "info")
        },
        "confidenceCounts": {
            confidence: sum(1 for item in findings if item.get("confidence") == confidence)
            for confidence in ("confirmed", "candidate", "unknown")
        },
        "paths": paths,
        "findings": findings,
    }


def _md(value: Any) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(snapshot: dict[str, Any], analysis: dict[str, Any]) -> str:
    flow = snapshot.get("flow", {})
    lines = [
        "# 百度智能云对等连接连通性配置诊断报告",
        "",
        f"- 快照时间：{_md(snapshot.get('generatedAt'))}",
        f"- 报告时间：{_md(analysis.get('generatedAt'))}",
        f"- 模式：{_md(analysis.get('summary', {}).get('mode'))}",
        "- 安全边界：仅执行 GET 配置查询；未修改资源，也未发送业务探测流量。",
        "- 流量参数：source={}，destination={}，protocol={}，port={}".format(
            _md(flow.get("sourceIp")),
            _md(flow.get("destinationIp")),
            _md(flow.get("protocol")),
            _md(flow.get("port")),
        ),
        "",
        "## 发现范围",
        "",
        "| 地域 | 列表状态 | 返回连接数 | 查询数 | 失败查询 |",
        "|---|---|---:|---:|---:|",
    ]
    for region, discovery in sorted(snapshot.get("discoveryRegions", {}).items()):
        coverage = discovery.get("coverage", {})
        lines.append(
            "| {} | {} | {} | {} | {} |".format(
                _md(region),
                _md(coverage.get("status", "unknown")),
                _md(coverage.get("count", 0)),
                _md(coverage.get("queries", 0)),
                _md(coverage.get("failedQueries", 0)),
            )
        )

    lines.extend(
        [
            "",
            "## 连接与端点",
            "",
            "| 连接 ID | 状态 | 本端地域/VPC | 本端接口 | 对端地域/VPC | 对端接口 | 对端方向 |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for diagnosis in snapshot.get("diagnoses", []):
        peer = diagnosis.get("peerConnection", {})
        local = diagnosis.get("endpoints", {}).get("local", {})
        remote = diagnosis.get("endpoints", {}).get("peer", {})
        lines.append(
            "| {} | {} | {}/{} | {} | {}/{} | {} | {} |".format(
                _md(_peer_id(peer)),
                _md(peer.get("status")),
                _md(local.get("region")),
                _md(local.get("vpcId")),
                _md(local.get("interfaceId")),
                _md(remote.get("region")),
                _md(remote.get("vpcId")),
                _md(remote.get("interfaceId")),
                _md(diagnosis.get("remoteOrientation", {}).get("status")),
            )
        )

    lines.extend(
        [
            "",
            "## 端点查询覆盖率",
            "",
            "| 连接 ID | 端点 | 地域 | 资源 | 状态 | 数量 | 查询数 | 失败查询 |",
            "|---|---|---|---|---|---:|---:|---:|",
        ]
    )
    for diagnosis in snapshot.get("diagnoses", []):
        peer_id = _peer_id(diagnosis.get("peerConnection", {}))
        for side in ("local", "peer"):
            endpoint = diagnosis.get("endpoints", {}).get(side, {})
            for resource in RESOURCE_KEYS:
                coverage = endpoint.get("coverage", {}).get(resource, {})
                lines.append(
                    "| {} | {} | {} | {} | {} | {} | {} | {} |".format(
                        _md(peer_id),
                        _md(side),
                        _md(endpoint.get("region")),
                        _md(resource),
                        _md(coverage.get("status", "unknown")),
                        _md(coverage.get("count", 0)),
                        _md(coverage.get("queries", 0)),
                        _md(coverage.get("failedQueries", 0)),
                    )
                )

    lines.extend(
        [
            "",
            "## 路径判断",
            "",
            "| 连接 ID | 模式 | 源子网 | 目的子网 | 去向路由 | 回向路由 |",
            "|---|---|---|---|---|---|",
        ]
    )
    for path in analysis.get("paths", []):
        lines.append(
            "| {} | {} | {} | {} | {} | {} |".format(
                _md(path.get("peerConnId")),
                _md(path.get("mode")),
                _md(path.get("sourceSubnetId")),
                _md(path.get("destinationSubnetId")),
                _md(path.get("forwardRoute")),
                _md(path.get("reverseRoute")),
            )
        )

    counts = analysis.get("findingCounts", {})
    confidence = analysis.get("confidenceCounts", {})
    lines.extend(
        [
            "",
            "## 诊断发现",
            "",
            f"高：{counts.get('high', 0)}；中：{counts.get('medium', 0)}；低：{counts.get('low', 0)}；信息：{counts.get('info', 0)}。",
            f"已确认：{confidence.get('confirmed', 0)}；候选：{confidence.get('candidate', 0)}；未知：{confidence.get('unknown', 0)}。",
            "",
            "| 严重度 | 置信度 | 规则 | 连接 ID | 端点 | 事实 | 判断 |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for finding in analysis.get("findings", []):
        lines.append(
            "| {} | {} | {} | {} | {} | {} | {} |".format(
                _md(finding.get("severity")),
                _md(finding.get("confidence")),
                _md(finding.get("ruleId")),
                _md(finding.get("peerConnId")),
                _md(finding.get("side")),
                _md(finding.get("fact")),
                _md(finding.get("interpretation")),
            )
        )
    if not analysis.get("findings"):
        lines.append(
            "| info | unknown | NONE | - | - | 在成功查询且可判定的范围内未发现配置阻断 | 不代表数据面或应用一定正常 |"
        )

    lines.extend(
        [
            "",
            "## 结论边界与下一步",
            "",
            "- 先处理 confirmed，再验证 candidate；unknown 必须补充权限、对端视角或流量参数后复查。",
            "- 路由命中只证明控制面配置可能选中对等连接，不证明报文已到达实例。",
            "- 普通安全组判断依赖 IP 到 ENI 的映射；企业安全组、地址组、主机防火墙和应用监听可能继续影响结果。",
            "- 跨账号对端不可见时，请由对端账号运行同一只读诊断并交换脱敏后的规则证据，不要共享长期 AK/SK。",
            "- 本报告不执行任何修复；所有变更需单独评审。",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    output_dir: Path,
    snapshot: dict[str, Any],
    analysis: dict[str, Any],
    *,
    overwrite: bool,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = output_dir / "snapshot.json"
    report_path = output_dir / "report.md"
    if not overwrite:
        existing = [path for path in (snapshot_path, report_path) if path.exists()]
        if existing:
            raise FileExistsError(
                "Refusing to overwrite existing output: " + ", ".join(str(path) for path in existing)
            )
    payload = dict(snapshot)
    payload["analysis"] = analysis
    with snapshot_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(snapshot, analysis))
    return snapshot_path, report_path


def _flow_from_args(args: argparse.Namespace, base: dict[str, Any] | None = None) -> dict[str, Any]:
    flow = dict(base or {})
    overrides = {
        "sourceIp": args.source_ip,
        "destinationIp": args.destination_ip,
        "protocol": args.protocol,
        "port": args.port,
    }
    for key, value in overrides.items():
        if value is not None:
            flow[key] = value
    source = _optional_string(flow.get("sourceIp"))
    destination = _optional_string(flow.get("destinationIp"))
    if bool(source) != bool(destination):
        raise ValueError("--source-ip and --destination-ip must be provided together")
    if source and destination:
        source_address = ipaddress.ip_address(source)
        destination_address = ipaddress.ip_address(destination)
        if source_address.version != destination_address.version:
            raise ValueError("Source and destination IP versions must match")
    protocol = _optional_string(flow.get("protocol"))
    if protocol:
        protocol = protocol.lower()
        if protocol not in {"tcp", "udp", "icmp", "icmpv6", "all"}:
            raise ValueError("Protocol must be tcp, udp, icmp, icmpv6, or all")
        flow["protocol"] = protocol
    port = flow.get("port")
    if port is not None:
        if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
            raise ValueError("Port must be an integer from 1 to 65535")
        if protocol not in {"tcp", "udp"}:
            raise ValueError("Port is valid only with tcp or udp")
    if (protocol or port is not None) and not (source and destination):
        raise ValueError("Protocol and port require source and destination IPs")
    return {
        key: flow.get(key)
        for key in ("sourceIp", "destinationIp", "protocol", "port")
        if flow.get(key) is not None
    }


def self_test() -> None:
    sample = Path(__file__).resolve().parents[1] / "examples" / "sample-connectivity-snapshot.json"
    snapshot = load_snapshot(sample)
    analysis = analyze_snapshot(snapshot)
    rule_ids = {item.get("ruleId") for item in analysis.get("findings", [])}
    expected = {"ROUTE-002", "ROUTE-005", "SG-002", "ACL-002"}
    missing = expected - rule_ids
    if missing:
        raise AssertionError(f"Sample analysis missed expected rules: {sorted(missing)}")
    if "ROUTE-001" in rule_ids or "SG-001" in rule_ids or "ACL-001" in rule_ids:
        raise AssertionError("Sample produced a false local-side blocking result")

    client = ReadOnlyBceClient("https://bcc.bj.baidubce.com", "ak", "sk")
    try:
        client.request_json("/v1/peerconn", method="POST")
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

    page_calls: list[dict[str, Any]] = []

    def fake_pages(path: str, params: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
        page_calls.append(dict(params or {}))
        if params and params.get("marker") == "next":
            return {"peerConns": [{"peerConnId": "peer-2"}], "isTruncated": False}
        return {
            "peerConns": [{"peerConnId": "peer-1"}],
            "isTruncated": True,
            "nextMarker": "next",
        }

    client.request_json = fake_pages  # type: ignore[method-assign]
    pages = client.paginate("/v1/peerconn", ("peerConns",))
    if len(pages) != 2 or len(page_calls) != 2 or page_calls[1].get("marker") != "next":
        raise AssertionError("Pagination did not follow nextMarker exactly once")

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

    route = {
        "sourceAddress": "10.0.0.0/8",
        "destinationAddress": "192.168.0.0/16",
        "nexthopType": "peerConn",
        "nexthopId": "qpif-correct",
    }
    if not _route_has_expected_peer(route, "qpif-correct"):
        raise AssertionError("Route next-hop matcher rejected the endpoint interface")
    if _route_has_expected_peer(route, "peerconn-wrong-kind"):
        raise AssertionError("Route next-hop matcher accepted a connection ID")

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
        "Self-test passed: fixture diagnosis, GET-only and endpoint guards, pagination, "
        "route-interface matching, credential-file guards, and deterministic signer"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only Baidu AI Cloud VPC peering connectivity diagnosis"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--input", type=Path, help="Analyze an existing normalized snapshot JSON")
    mode.add_argument("--self-test", action="store_true", help="Run local tests without network access")
    parser.add_argument("--regions", help="Comma-separated local BCE regions for live discovery")
    parser.add_argument("--peer-conn-id", help="Diagnose only this peer connection ID")
    parser.add_argument("--source-ip", help="Source private IP in the local endpoint VPC")
    parser.add_argument("--destination-ip", help="Destination private IP in the peer endpoint VPC")
    parser.add_argument("--protocol", help="tcp, udp, icmp, icmpv6, or all")
    parser.add_argument("--port", type=int, help="Destination port for tcp or udp")
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
    parser.add_argument("--output-dir", type=Path, help="Directory for snapshot.json and report.md")
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
        if args.input:
            snapshot = load_snapshot(args.input)
            snapshot["flow"] = _flow_from_args(args, snapshot.get("flow", {}))
        else:
            flow = _flow_from_args(args)
            if flow.get("sourceIp") and not args.peer_conn_id:
                raise ValueError("Precise flow mode requires --peer-conn-id in live collection")
            snapshot = collect_live(args, flow)
        analysis = analyze_snapshot(snapshot)
        snapshot_path, report_path = write_outputs(
            args.output_dir, snapshot, analysis, overwrite=args.overwrite
        )
        print(f"Snapshot: {snapshot_path}")
        print(f"Report: {report_path}")
        has_high_coverage_gap = any(
            item.get("severity") == "high" and str(item.get("ruleId", "")).startswith("COV-")
            for item in analysis.get("findings", [])
        )
        return 2 if has_high_coverage_gap else 0
    except (
        ApiFailure,
        FileExistsError,
        OSError,
        ValueError,
        AssertionError,
        json.JSONDecodeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
