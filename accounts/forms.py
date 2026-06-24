from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class InviteRegistrationForm(UserCreationForm):
    invite_code = forms.CharField(max_length=64, label="Codice invito")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "invite_code", "password1", "password2")

    def clean_invite_code(self):
        from django.conf import settings
        code = self.cleaned_data["invite_code"]
        valid = getattr(settings, "INVITE_CODE", None)
        if not valid or code != valid:
            raise forms.ValidationError("Codice invito non valido.")
        return code


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("bio", "avatar")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
        }
