import re
from decimal import Decimal

from django import forms

from .models import Portfolio

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.\-]{1,12}$")


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "currency", "is_public"]
        labels = {"is_public": "Visible to friends"}

    def clean_currency(self):
        return self.cleaned_data["currency"].upper()


class PortfolioSettingsForm(PortfolioForm):
    # Currency is fixed once a portfolio exists; changing it would relabel every past trade.
    class Meta(PortfolioForm.Meta):
        fields = ["name", "is_public"]


class TradeForm(forms.Form):
    SIDE_CHOICES = [("BUY", "Buy"), ("SELL", "Sell")]

    side = forms.ChoiceField(choices=SIDE_CHOICES, initial="BUY", widget=forms.RadioSelect)
    symbol = forms.CharField(max_length=12)
    quantity = forms.DecimalField(max_digits=18, decimal_places=6, min_value=Decimal("0.000001"))
    price = forms.DecimalField(max_digits=14, decimal_places=4, min_value=Decimal("0.0001"), label="Price per share")
    fee = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False, initial=0)
    use_cash = forms.BooleanField(
        required=False, initial=True, label="Pay from cash",
        help_text="Untick to record shares you bought outside this app.",
    )

    def clean_symbol(self):
        symbol = self.cleaned_data["symbol"].upper().strip()
        if not SYMBOL_PATTERN.match(symbol):
            raise forms.ValidationError("Use letters, numbers, dots or dashes, e.g. AAPL or BRK.B.")
        return symbol

    def clean_fee(self):
        return self.cleaned_data["fee"] or Decimal("0")


class CashForm(forms.Form):
    ACTION_CHOICES = [("DEPOSIT", "Deposit"), ("WITHDRAW", "Withdraw")]

    action = forms.ChoiceField(choices=ACTION_CHOICES, initial="DEPOSIT", widget=forms.RadioSelect)
    amount = forms.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"))
