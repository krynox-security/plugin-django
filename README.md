# Krynox Captcha for Django

Privacy-first, proof-of-work CAPTCHA as a Django form field. No cookies, no puzzles.

## Install

```bash
pip install django-krynox-captcha
```

Add your keys to `settings.py`:

```python
KRYNOX_SITE_KEY = "kcpt_live_xxx"
KRYNOX_SECRET_KEY = "kcps_live_xxx"
# optional, for self-hosting:
# KRYNOX_API_HOST = "https://api.krynox.net"
# KRYNOX_CDN_HOST = "https://cdn.krynox.net"
```

(No need to add to `INSTALLED_APPS` — it's just a form field.)

## Use

```python
from django import forms
from krynox_captcha import KrynoxCaptchaField

class SignupForm(forms.Form):
    email = forms.EmailField()
    captcha = KrynoxCaptchaField()

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        if request is not None:
            self.fields["captcha"].set_request(request)
```

Instantiate it with `SignupForm(request.POST, request=request)`. The field forwards
`REMOTE_ADDR`; configure your WSGI/ASGI server's trusted-proxy handling rather than
reading an untrusted `X-Forwarded-For` header directly.

Render the form as usual (`{{ form }}`) — the field outputs the widget script and the
`<krynox-captcha>` element. On submit, `form.is_valid()` verifies the solution
server-to-server against `/siteverify`; failures surface as a field error.

### Verify manually

```python
from krynox_captcha import verify

result = verify(settings.KRYNOX_SECRET_KEY, request.POST.get("krynox-captcha"),
                remoteip=request.META.get("REMOTE_ADDR"))
if not result["success"]:
    ...
# result["risk"] => "low" | "medium" | "high"
# result["reasons"] => ["tor-exit", ...]; result["agent"]; result["human"]
```

`verify()` returns the full contract — `success`, `score`, `risk`, `hostname`, `challenge_ts`,
`error_codes`, `reasons`, `agent` (`{verified, name, allowlisted}` or `None`), `human`
(`{attested, method, issuer}` or `None`). Transient failures (network / 429 / 5xx) are retried
automatically (`retries=`, default 2) with a per-verify idempotency key.

## Honeypot

Enable **Honeypot** for the site in the Krynox dashboard and the widget injects an invisible decoy
field (`krynox-hp`) that only bots fill in. `KrynoxCaptchaField` forwards it to `/siteverify` as
`honeypot` automatically — no code change needed. The data plane then floors the score (report mode)
or rejects with `honeypot-tripped` (enforce mode). See the
[Honeypot docs](https://docs.krynox.net/server-side/honeypot/).

## License

MIT. Built for [Krynox Captcha](https://krynox.net) · docs: <https://docs.krynox.net>
