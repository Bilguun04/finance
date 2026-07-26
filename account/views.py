import json
from datetime import timedelta

from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from firebase_admin import auth as firebase_auth

from .decorators import firebase_login_required
from .firestore import create_profile_if_missing, get_profile, update_profile
from .forms import ProfileEditForm
from .middleware import SESSION_COOKIE_NAME

SESSION_MAX_AGE = timedelta(days=14)


def login_page(request):
    if request.firebase_user:
        return redirect("core:dashboard")
    next_url = request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = ""
    return render(request, "account/login.html", {"next": next_url})


def signup_page(request):
    if request.firebase_user:
        return redirect("core:dashboard")
    return render(request, "account/signup.html")


@require_POST
def create_session(request):
    try:
        body = json.loads(request.body)
        id_token = body["idToken"]
    except (json.JSONDecodeError, KeyError):
        return HttpResponseBadRequest("Missing idToken")

    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except (firebase_auth.InvalidIdTokenError, ValueError):
        return HttpResponseBadRequest("Invalid idToken")

    uid = decoded["uid"]
    email = decoded.get("email", "")
    display_name = decoded.get("name") or (email.split("@")[0] if email else "")
    create_profile_if_missing(uid, display_name=display_name, email=email)

    session_cookie = firebase_auth.create_session_cookie(id_token, expires_in=SESSION_MAX_AGE)
    response = JsonResponse({"ok": True})
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_cookie,
        max_age=int(SESSION_MAX_AGE.total_seconds()),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )
    return response


@require_POST
def logout_view(request):
    cookie = request.COOKIES.get(SESSION_COOKIE_NAME)
    if cookie:
        try:
            decoded = firebase_auth.verify_session_cookie(cookie)
            firebase_auth.revoke_refresh_tokens(decoded["uid"])
        except (firebase_auth.InvalidSessionCookieError, ValueError):
            pass

    response = redirect("core:index")
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@firebase_login_required
def profile_view(request):
    profile = get_profile(request.firebase_user["uid"]) or {}
    return render(request, "account/profile.html", {"profile": profile})


@firebase_login_required
def profile_edit(request):
    uid = request.firebase_user["uid"]
    profile = get_profile(uid) or {}
    if request.method == "POST":
        form = ProfileEditForm(request.POST)
        if form.is_valid():
            update_profile(uid, form.cleaned_data["display_name"], form.cleaned_data["bio"])
            return redirect("account:profile")
    else:
        form = ProfileEditForm(initial=profile)

    return render(request, "account/profile_edit.html", {"form": form})
