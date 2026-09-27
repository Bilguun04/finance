from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required
from portfolio.services import get_or_create_portfolio
from social.services import friend_uids, incoming_requests


def index(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/landing.html")


@login_required
def dashboard(request):
    uid = request.user.pk
    portfolio = get_or_create_portfolio(uid)
    friend_count = len(friend_uids(uid))
    pending_count = len(incoming_requests(uid))
    return render(
        request,
        "core/dashboard.html",
        {
            "portfolio": portfolio,
            "friend_count": friend_count,
            "pending_count": pending_count,
        },
    )
