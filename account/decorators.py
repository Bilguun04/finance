from functools import wraps
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


def firebase_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.firebase_user is None:
            login_url = reverse(settings.LOGIN_URL)
            return redirect(f"{login_url}?{urlencode({'next': request.path})}")
        return view_func(request, *args, **kwargs)

    return wrapper
