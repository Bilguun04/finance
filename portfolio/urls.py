from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.portfolio_detail, name="detail"),
    path("holdings/add/", views.holding_add, name="holding_add"),
    path("holdings/<str:holding_id>/edit/", views.holding_edit, name="holding_edit"),
    path("holdings/<str:holding_id>/delete/", views.holding_delete, name="holding_delete"),
]
