from django import forms


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    country = forms.CharField(max_length=80, required=False)

    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.save(update_fields=["first_name"])
        profile = user.profile
        profile.country = self.cleaned_data.get("country", "")
        profile.save(update_fields=["country"])
