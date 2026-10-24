from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import SignupForm


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)

    return render(request, "account/signup.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    return render(request, "account/profile.html")
