from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("market/snapshot/", views.market_snapshot, name="market_snapshot"),
    path("market/pulse/", views.market_pulse, name="market_pulse"),
]
