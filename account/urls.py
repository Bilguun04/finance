from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("signup/", views.signup_page, name="signup"),
    path("login/", views.login_page, name="login"),
    path("session/", views.create_session, name="create_session"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]
