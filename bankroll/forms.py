from django import forms
from .models import Session

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['host', 'format', 'type', 'stakes', 'session_start', 'session_end', 'buyin', 'buyout']