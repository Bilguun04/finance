from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/trade/", views.trade, name="trade"),
    path("<int:pk>/cash/", views.cash, name="cash"),
    path("<int:pk>/refresh/", views.refresh_prices, name="refresh"),
    path("<int:pk>/settings/", views.settings, name="settings"),
    path("<int:pk>/delete/", views.delete, name="delete"),
]
