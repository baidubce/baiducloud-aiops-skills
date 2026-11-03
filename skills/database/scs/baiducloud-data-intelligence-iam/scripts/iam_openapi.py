#!/usr/bin/env python3
"""IAM-signed (BCE Auth v1) HTTP client for Baidu Cloud IAM OpenAPI.

Thin entry: all signing, redaction, credential and request logic lives in the
shared ``bce_openapi_core`` module; here we only declare the IAM endpoint.
GET/HEAD and --read-only (query-style POST) requests run freely; writes require --allow-write.
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

# IAM exposes a single global endpoint; region is validated but not used to
# build the host.
SERVICE = _core.ServiceConfig(
    label="IAM",
    endpoint_env="BAIDU_IAM_ENDPOINT",
    protocol_env="BAIDU_IAM_PROTOCOL",
    default_endpoint="iam.bj.baidubce.com",
    host_template="iam.bj.baidubce.com",
    regional=False,
)

# Re-export shared symbols so tests and callers keep the historical surface.
BceIamAuth = _core.BceIamAuth
redact = _core.redact
load_credentials = _core.load_credentials
parse_query = _core.parse_query


def resolve_endpoint(region=None):
    """Return the IAM endpoint host (global); region is validated but ignored."""
    return _core.resolve_endpoint(SERVICE, region)


def resolve_protocol():
    """Return the request protocol (https by default)."""
    return _core.resolve_protocol(SERVICE)


def run_request(method, path, **kwargs):
    """Sign and send one IAM OpenAPI request; return {status, body[, headers]}."""
    return _core.run_request(SERVICE, method, path, **kwargs)


def main(argv=None) -> int:
    """CLI entry: build, sign, send one IAM OpenAPI request; print JSON result."""
    return _core.main(SERVICE, argv)


if __name__ == "__main__":
    raise SystemExit(main())
