from django import forms


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    country = forms.CharField(max_length=80)
    phone = forms.CharField(max_length=30)
    whatsapp = forms.CharField(max_length=30)

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
