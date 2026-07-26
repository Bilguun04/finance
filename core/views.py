from django.shortcuts import redirect, render

from account.decorators import firebase_login_required
from portfolio.firestore import get_or_create_portfolio
from social.firestore import friend_uids, incoming_requests


def index(request):
    if request.firebase_user:
        return redirect("core:dashboard")
    return render(request, "core/landing.html")


@firebase_login_required
def dashboard(request):
    uid = request.firebase_user["uid"]
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
