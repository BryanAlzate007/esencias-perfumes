from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.core import context

from .captcha import verify_recaptcha


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    country = forms.CharField(max_length=80)
    phone = forms.CharField(max_length=30)
    whatsapp = forms.CharField(max_length=30)
    captcha = forms.CharField(required=False)

    def clean_captcha(self):
        if getattr(self, "sociallogin", None):
            return ""
        token = (self.cleaned_data.get("captcha") or "").strip()
        if not token or not verify_recaptcha(token, _client_ip()):
            raise forms.ValidationError(_("Confirma el captcha para crear la cuenta."))
        return token

    def signup(self, request, user):
        first_name = self.cleaned_data.get("first_name") or ""
        if first_name:
            user.first_name = first_name
            user.save(update_fields=["first_name"])
        profile = user.profile
        profile.country = self.cleaned_data.get("country", "")
        profile.phone = self.cleaned_data.get("phone", "")
        profile.whatsapp = self.cleaned_data.get("whatsapp", "")
        profile.save(update_fields=["country", "phone", "whatsapp"])


def _client_ip():
    request = context.request
    if request is None:
        return ""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")
