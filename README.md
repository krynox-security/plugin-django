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
# KRYNOX_API_HOST = "https://api.krynox.id"
# KRYNOX_CDN_HOST = "https://cdn.krynox.id"
```

(No need to add to `INSTALLED_APPS` — it's just a form field.)

## Use

```python
from django import forms
from krynox_captcha import KrynoxCaptchaField

class SignupForm(forms.Form):
    email = forms.EmailField()
    captcha = KrynoxCaptchaField()
```

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
```

## License

MIT. Built for [Krynox Captcha](https://krynox.id) · docs: <https://krynox.id/docs>
