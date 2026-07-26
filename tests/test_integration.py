"""Real-HTTP integration tests for django-krynox-captcha.

A mock Krynox data plane (stdlib http.server) runs on a real local socket;
KrynoxCaptchaField / client.verify() talk to it over actual HTTP. Requires
only Django (settings are configured in-process below) — run with:

    python -m unittest discover -s tests -t .
"""

from __future__ import annotations

import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        INSTALLED_APPS=[],
        DATABASES={},
        KRYNOX_SITE_KEY="kcpt_test",
        KRYNOX_SECRET_KEY="kcps_test",
        KRYNOX_API_HOST="http://127.0.0.1:1",  # overridden per-test
    )
    django.setup()

from django import forms  # noqa: E402
from django.test import override_settings  # noqa: E402

from krynox_captcha import verify  # noqa: E402
from krynox_captcha.fields import KrynoxCaptchaField  # noqa: E402

SUCCESS_BODY = {
    "success": True,
    "score": 0.92,
    "risk": "low",
    "hostname": "example.com",
    "challenge_ts": "2026-07-27T00:00:00Z",
    "error-codes": [],
    "reasons": ["pow-valid"],
    "agent": {"verified": True, "name": "example-agent", "allowlisted": False},
    "human": {"attested": True, "method": "pat", "issuer": "apple"},
}


class MockPlane:
    """Scripted mock of the Krynox data plane on a real HTTP socket.

    Every received POST body is recorded; responses come from a per-test
    script of (status, body) entries, or ("hang", seconds) for timeouts.
    """

    def __init__(self):
        self.requests = []
        self.script = []
        plane = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get("content-length", 0)))
                try:
                    body = json.loads(raw.decode())
                except ValueError:
                    body = raw.decode()
                plane.requests.append(
                    {
                        "path": self.path,
                        "content_type": self.headers.get("content-type"),
                        "body": body,
                    }
                )
                step = plane.script.pop(0) if plane.script else (200, SUCCESS_BODY)
                status, payload = step
                if status == "hang":
                    time.sleep(payload)
                    return
                data = payload if isinstance(payload, str) else json.dumps(payload)
                data = data.encode()
                self.send_response(status)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):  # silence per-request logging
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:%d" % self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class SignupForm(forms.Form):
    captcha = KrynoxCaptchaField()


class PlaneTestCase(unittest.TestCase):
    def setUp(self):
        self.plane = MockPlane()
        self.addCleanup(self.plane.stop)
        override = override_settings(KRYNOX_API_HOST=self.plane.url)
        override.enable()
        self.addCleanup(override.disable)


class KrynoxCaptchaFieldTests(PlaneTestCase):
    def test_valid_token_form_is_valid_and_plane_receives_payload(self):
        self.plane.script = [(200, SUCCESS_BODY)]
        form = SignupForm(data={"krynox-captcha": "tok_solved"})

        self.assertTrue(form.is_valid(), form.errors)

        self.assertEqual(len(self.plane.requests), 1)
        req = self.plane.requests[0]
        self.assertEqual(req["path"], "/siteverify")
        self.assertEqual(req["content_type"], "application/json")
        self.assertEqual(
            list(req["body"].keys()),
            ["secret", "response", "remoteip", "honeypot", "idempotency_key"],
        )
        self.assertEqual(req["body"]["secret"], "kcps_test")
        self.assertEqual(req["body"]["response"], "tok_solved")
        self.assertIsNone(req["body"]["remoteip"])
        # no "krynox-hp" key submitted -> honeypot forwarded as null
        self.assertIsNone(req["body"]["honeypot"])
        # default retries (2) > 0 -> idempotency key always sent
        self.assertRegex(req["body"]["idempotency_key"], r"^[0-9a-f]{32}$")

    def test_invalid_token_raises_krynox_validation_error(self):
        self.plane.script = [
            (200, {"success": False, "error-codes": ["invalid-input-response"]})
        ]
        form = SignupForm(data={"krynox-captcha": "tok_bad"})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["captcha"],
            ["CAPTCHA verification failed. Please try again."],
        )
        self.assertEqual(form.errors.as_data()["captcha"][0].code, "krynox")
        self.assertEqual(len(self.plane.requests), 1)

    def test_missing_token_required_error_without_plane_hit(self):
        form = SignupForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()["captcha"][0].code, "required")
        self.assertEqual(len(self.plane.requests), 0)

    def test_filled_honeypot_is_forwarded_and_fails_the_form(self):
        self.plane.script = [
            (200, {"success": False, "error-codes": ["honeypot-tripped"]})
        ]
        form = SignupForm(
            data={"krynox-captcha": "tok_solved", "krynox-hp": "gotcha"}
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()["captcha"][0].code, "krynox")
        self.assertEqual(self.plane.requests[0]["body"]["honeypot"], "gotcha")

    def test_set_request_forwards_remote_addr_as_remoteip(self):
        self.plane.script = [(200, SUCCESS_BODY)]
        form = SignupForm(data={"krynox-captcha": "tok_solved"})
        request = SimpleNamespace(META={"REMOTE_ADDR": "198.51.100.7"})
        form.fields["captcha"].set_request(request)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(self.plane.requests[0]["body"]["remoteip"], "198.51.100.7")


class ClientVerifyTests(PlaneTestCase):
    def test_retries_500_then_succeeds_with_same_idempotency_key(self):
        self.plane.script = [(500, "boom"), (200, SUCCESS_BODY)]

        result = verify("kcps_test", "tok_solved", api_host=self.plane.url)

        self.assertTrue(result["success"])
        self.assertEqual(result["score"], 0.92)
        self.assertEqual(result["risk"], "low")
        self.assertEqual(result["hostname"], "example.com")
        self.assertEqual(result["reasons"], ["pow-valid"])
        self.assertEqual(
            result["agent"],
            {"verified": True, "name": "example-agent", "allowlisted": False},
        )
        self.assertEqual(
            result["human"], {"attested": True, "method": "pat", "issuer": "apple"}
        )
        self.assertEqual(len(self.plane.requests), 2)
        keys = [r["body"]["idempotency_key"] for r in self.plane.requests]
        self.assertIsNotNone(keys[0])
        self.assertEqual(keys[0], keys[1])

    def test_timeout_returns_request_failed(self):
        self.plane.script = [("hang", 3)]

        started = time.monotonic()
        result = verify(
            "kcps_test", "tok_solved", api_host=self.plane.url, timeout=0.3, retries=0
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["error_codes"], ["request-failed"])
        self.assertLess(time.monotonic() - started, 2.5)
        self.assertEqual(len(self.plane.requests), 1)
        # retries=0 -> no idempotency key
        self.assertIsNone(self.plane.requests[0]["body"]["idempotency_key"])

    def test_exhausted_retries_returns_request_failed(self):
        self.plane.script = [(500, "boom")] * 3

        result = verify("kcps_test", "tok_solved", api_host=self.plane.url)

        self.assertFalse(result["success"])
        self.assertEqual(result["error_codes"], ["request-failed"])
        # default retries=2 -> exactly 3 attempts
        self.assertEqual(len(self.plane.requests), 3)

    def test_missing_response_short_circuits_without_http(self):
        for empty in ("", None):
            result = verify("kcps_test", empty, api_host=self.plane.url)
            self.assertFalse(result["success"])
            self.assertEqual(result["error_codes"], ["missing-input-response"])
        self.assertEqual(len(self.plane.requests), 0)


if __name__ == "__main__":
    unittest.main()
