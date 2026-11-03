#!/usr/bin/env python3
"""IAM-signed (BCE Auth v1) HTTP client for Baidu Cloud BCM OpenAPI.

BCM = 云监控 (Cloud Monitor): metrics, alarm configs/policies, dashboards,
notification groups, events for cloud resources.

Thin entry: all signing, redaction, credential and request logic lives in the
shared ``bce_openapi_core`` module; here we only declare the BCM endpoint.
GET/HEAD and --read-only (query-style POST) requests run freely; writes require --allow-write.

Note: BCM 所有 region 支持 HTTP，仅武汉(wh)/上海(sh) 支持 HTTPS，故默认协议为 http；
访问 wh/sh 时可用 BAIDU_BCM_PROTOCOL=https 覆盖。
"""
from __future__ import annotations

import os
import sys

# Resolve the shared core in both layouts: deployed (vendored next to this file)
# and source tree (skills/_common/). Same-dir is tried first so the deployed
# skill stays self-contained.
_HERE = os.path.dirname(os.path.abspath(__file__))
for _candidate in (_HERE, os.path.join(_HERE, "..", "..", "_common")):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import bce_openapi_core as _core  # noqa: E402
import requests  # noqa: E402 — exposed as module attribute for test monkeypatching

SERVICE = _core.ServiceConfig(
    label="BCM",
    endpoint_env="BAIDU_BCM_ENDPOINT",
    protocol_env="BAIDU_BCM_PROTOCOL",
    default_endpoint="bcm.bj.baidubce.com",
    host_template="bcm.{region}.baidubce.com",
    regional=True,
    default_protocol="http",  # BCM 多数 region 仅支持 HTTP；wh/sh 可设 BAIDU_BCM_PROTOCOL=https
)

# Re-export shared symbols so tests and callers keep the historical surface.
BceIamAuth = _core.BceIamAuth
redact = _core.redact
load_credentials = _core.load_credentials
parse_query = _core.parse_query


def resolve_endpoint(region=None):
    """Return the BCM endpoint host for a region, honoring env override."""
    return _core.resolve_endpoint(SERVICE, region)


def resolve_protocol():
    """Return the request protocol (http by default for BCM)."""
    return _core.resolve_protocol(SERVICE)


def run_request(method, path, **kwargs):
    """Sign and send one BCM OpenAPI request; return {status, body[, headers]}."""
    return _core.run_request(SERVICE, method, path, **kwargs)


def main(argv=None) -> int:
    """CLI entry: build, sign, send one BCM OpenAPI request; print JSON result."""
    return _core.main(SERVICE, argv)


if __name__ == "__main__":
    raise SystemExit(main())
