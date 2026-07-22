"""Form field that verifies the Krynox Captcha solution server-side."""

from __future__ import annotations

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .client import verify
from .widgets import KrynoxCaptchaWidget


class KrynoxCaptchaField(forms.Field):
    """Drop into any Django form::

        class SignupForm(forms.Form):
            email = forms.EmailField()
            captcha = KrynoxCaptchaField()
    """

    widget = KrynoxCaptchaWidget
    default_error_messages = {
        "krynox": _("CAPTCHA verification failed. Please try again."),
    }

    def __init__(self, *args, remoteip=None, **kwargs):
        self.remoteip = remoteip
        kwargs.setdefault("label", "")
        super().__init__(*args, **kwargs)

    def set_request(self, request):
        """Bind a request to this form instance using Django's socket peer IP.

        If Django is behind a proxy, configure the web server/framework to expose
        a trusted peer. Raw X-Forwarded-For is intentionally not read here.
        """
        self.remoteip = request.META.get("REMOTE_ADDR") if request is not None else None
        return self

    def _remoteip(self):
        return self.remoteip() if callable(self.remoteip) else self.remoteip

    def clean(self, value):
        value = super().clean(value)  # honours `required`
        secret = getattr(settings, "KRYNOX_SECRET_KEY", "")
        api = getattr(settings, "KRYNOX_API_HOST", "https://api.krynox.net")
        honeypot = getattr(self.widget, "honeypot", None)
        result = verify(
            secret,
            value,
            remoteip=self._remoteip(),
            api_host=api,
            honeypot=honeypot,
        )
        if not result.get("success"):
            raise ValidationError(self.error_messages["krynox"], code="krynox")
        return value
