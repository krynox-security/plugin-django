"""Server-side verification client for Krynox Captcha (stdlib only)."""

from __future__ import annotations

import json
import secrets
import time
import urllib.error
import urllib.request
from typing import Any, Optional


def verify(
    secret: str,
    response: Optional[str],
    *,
    api_host: str = "https://api.krynox.net",
    timeout: float = 5.0,
    remoteip: Optional[str] = None,
    honeypot: Optional[str] = None,
    retries: int = 2,
) -> dict:
    """Verify a solved token against POST /siteverify.

    Returns a dict: ``{success, score, risk, hostname, challenge_ts, error_codes, reasons,
    agent, human}``. ``agent``/``human`` are nested dicts (or ``None``) carrying the verified
    AI-agent / attested-human identity when the integrator forwards one.

    Transient failures (network / 429 / 5xx) are retried; a retried verify carries an idempotency
    key so a retried single-use token replays the first outcome instead of failing.
    """
    if not response:
        return _fail(["missing-input-response"])

    endpoint = api_host.rstrip("/") + "/siteverify"
    key = secrets.token_hex(16) if retries > 0 else None
    body = json.dumps(
        {
            "secret": secret,
            "response": response,
            "remoteip": remoteip,
            "honeypot": honeypot,
            "idempotency_key": key,
        }
    ).encode()

    data = _post(endpoint, body, timeout=timeout, retries=retries)
    if not isinstance(data, dict):
        return _fail(["request-failed"])

    agent = data.get("agent")
    human = data.get("human")
    return {
        "success": data.get("success") is True,
        "score": data.get("score"),
        "risk": data.get("risk"),
        "hostname": data.get("hostname"),
        "challenge_ts": data.get("challenge_ts"),
        "error_codes": list(data.get("error-codes", []) or []),
        "reasons": list(data.get("reasons", []) or []),
        "agent": {
            "verified": agent.get("verified") is True,
            "name": agent.get("name"),
            "allowlisted": agent.get("allowlisted") is True,
        }
        if isinstance(agent, dict)
        else None,
        "human": {
            "attested": human.get("attested") is True,
            "method": human.get("method"),
            "issuer": human.get("issuer"),
        }
        if isinstance(human, dict)
        else None,
    }


def _post(endpoint: str, body: bytes, *, timeout: float, retries: int) -> Optional[Any]:
    """POST JSON, retrying transient failures (network / 429 / 5xx). Returns parsed JSON or None."""
    for attempt in range(retries + 1):
        req = urllib.request.Request(
            endpoint, data=body, headers={"content-type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            # A 4xx (other than 429) carries a JSON error body — return it, don't retry.
            if e.code != 429 and e.code < 500:
                try:
                    return json.loads(e.read().decode())
                except Exception:
                    return None
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        if attempt < retries:
            time.sleep(min(1.0, 0.1 * (2**attempt)))
    return None


def _fail(codes: list) -> dict:
    return {
        "success": False,
        "score": None,
        "risk": None,
        "hostname": None,
        "challenge_ts": None,
        "error_codes": codes,
        "reasons": [],
        "agent": None,
        "human": None,
    }
