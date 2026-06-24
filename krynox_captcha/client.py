"""Server-side verification client for Krynox Captcha (stdlib only)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional


def verify(
    secret: str,
    response: Optional[str],
    *,
    api_host: str = "https://api.krynox.id",
    timeout: float = 5.0,
    remoteip: Optional[str] = None,
) -> dict:
    """Verify a solved token against POST /siteverify.

    Returns a dict: {success, score, risk, hostname, challenge_ts, error_codes}.
    """
    if not response:
        return _fail(["missing-input-response"])

    endpoint = api_host.rstrip("/") + "/siteverify"
    body = json.dumps({"secret": secret, "response": response, "remoteip": remoteip}).encode()
    req = urllib.request.Request(
        endpoint, data=body, headers={"content-type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, ValueError, TimeoutError):
        return _fail(["request-failed"])

    if not isinstance(data, dict):
        return _fail(["request-failed"])

    return {
        "success": data.get("success") is True,
        "score": data.get("score"),
        "risk": data.get("risk"),
        "hostname": data.get("hostname"),
        "challenge_ts": data.get("challenge_ts"),
        "error_codes": list(data.get("error-codes", []) or []),
    }


def _fail(codes: list) -> dict:
    return {
        "success": False,
        "score": None,
        "risk": None,
        "hostname": None,
        "challenge_ts": None,
        "error_codes": codes,
    }
