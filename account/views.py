from django.contrib.auth import login
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm, SignupForm
from .services import create_profile_if_missing, get_profile, update_profile


def signup_page(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        create_profile_if_missing(user, display_name=user.email.split("@")[0])
        login(request, user)
        return redirect("core:dashboard")
    return render(request, "account/signup.html", {"form": form})


@login_required
def profile_view(request):
    profile = get_profile(request.user.pk) or {}
    return render(request, "account/profile.html", {"profile": profile})


@login_required
def profile_edit(request):
    uid = request.user.pk
    profile = get_profile(uid) or {}
    if request.method == "POST":
        form = ProfileEditForm(request.POST)
        if form.is_valid():
            update_profile(uid, form.cleaned_data["display_name"], form.cleaned_data["bio"])
            return redirect("account:profile")
    else:
        form = ProfileEditForm(initial=profile)

    return render(request, "account/profile_edit.html", {"form": form})
