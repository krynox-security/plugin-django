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

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label", "")
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)  # honours `required`
        secret = getattr(settings, "KRYNOX_SECRET_KEY", "")
        api = getattr(settings, "KRYNOX_API_HOST", "https://api.krynox.net")
        result = verify(secret, value, api_host=api)
        if not result.get("success"):
            raise ValidationError(self.error_messages["krynox"], code="krynox")
        return value
