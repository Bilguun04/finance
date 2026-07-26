from django import forms


class ProfileEditForm(forms.Form):
    display_name = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
