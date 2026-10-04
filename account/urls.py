from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import LoginForm

app_name = "account"

urlpatterns = [
    path("signup/", views.signup_page, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            authentication_form=LoginForm,
            template_name="account/login.html",
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]
