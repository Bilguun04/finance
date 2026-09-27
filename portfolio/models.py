from django.conf import settings
from django.db import models

from .dataclasses import ASSET_TYPE_CHOICES


class Portfolio(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolio")
	name = models.CharField(max_length=100, default="My Portfolio")
	created_at = models.DateTimeField(auto_now_add=True)


class Holding(models.Model):
	portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="holdings")
	symbol = models.CharField(max_length=20)
	name = models.CharField(max_length=100, blank=True)
	asset_type = models.CharField(max_length=10, choices=ASSET_TYPE_CHOICES, default="STOCK")
	quantity = models.DecimalField(max_digits=20, decimal_places=8)
	cost_basis_per_unit = models.DecimalField(max_digits=14, decimal_places=2)
	current_price = models.DecimalField(max_digits=14, decimal_places=2)

	class Meta:
		ordering = ["symbol"]

