"""Form widget that renders the <krynox-captcha> web component."""

from __future__ import annotations

from urllib.parse import quote

from django import forms
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe


class KrynoxCaptchaWidget(forms.Widget):
    """Renders the widget script + element. The web component injects the solved
    token as a hidden ``krynox-captcha`` field, which we read back on submit."""

    #: Honeypot decoy value captured on the last bind (the field reads it to forward).
    honeypot = None

    def value_from_datadict(self, data, files, name):
        # The widget always submits its solution under the fixed "krynox-captcha"
        # key, regardless of the Django form field's name. It also injects a hidden
        # "krynox-hp" decoy field (only bots fill it) — stash it here since this is
        # the one seam with access to the whole submitted data dict.
        self.honeypot = data.get("krynox-hp")
        return data.get("krynox-captcha")

    def render(self, name, value, attrs=None, renderer=None):
        cdn = getattr(settings, "KRYNOX_CDN_HOST", "https://cdn.krynox.net").rstrip("/")
        api = getattr(settings, "KRYNOX_API_HOST", "https://api.krynox.net").rstrip("/")
        site_key = getattr(settings, "KRYNOX_SITE_KEY", "")
        challenge = f"{api}/challenge?sitekey={quote(str(site_key), safe='')}"
        return mark_safe(
            f'<script async defer src="{escape(cdn)}/widget/krynox-captcha.js" type="module"></script>'
            f'<krynox-captcha challenge="{escape(challenge)}"></krynox-captcha>'
        )
