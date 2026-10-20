from django.urls import path

from . import views

app_name = "bankroll"

urlpatterns = [
	path("", views.dashboard, name="dashboard"),
	path("sessions/new/", views.add_session, name="add_session"),
	path("sessions/<int:session_id>/edit/", views.modify_session, name="modify_session"),
]
