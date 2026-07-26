from django import forms

from .dataclasses import ASSET_TYPE_CHOICES


class HoldingForm(forms.Form):
    symbol = forms.CharField(max_length=20)
    name = forms.CharField(max_length=100, required=False)
    asset_type = forms.ChoiceField(choices=ASSET_TYPE_CHOICES)
    quantity = forms.DecimalField(max_digits=20, decimal_places=8)
    cost_basis_per_unit = forms.DecimalField(max_digits=14, decimal_places=2)
    current_price = forms.DecimalField(max_digits=14, decimal_places=2)
