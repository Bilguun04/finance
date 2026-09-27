from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class SignupForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"] = forms.CharField(required=False)
        self.fields["username"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error("email", "An account with this email already exists.")
        if email:
            cleaned_data["username"] = email
        return cleaned_data


class ProfileEditForm(forms.Form):
    display_name = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
