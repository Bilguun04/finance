from urllib.parse import urlencode

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from account.decorators import firebase_login_required
from account.firestore import get_profile
from portfolio.firestore import get_or_create_portfolio

from . import firestore as sf


def _display_name(profile, fallback_uid):
    if not profile:
        return fallback_uid
    return profile.get("display_name") or profile.get("email") or fallback_uid


@firebase_login_required
def friend_search(request):
    uid = request.firebase_user["uid"]
    query = request.GET.get("q", "").strip()
    results = []
    if query:
        friend_ids = sf.friend_uids(uid)
        pending = sf.incoming_requests(uid) + sf.outgoing_requests(uid)
        pending_ids = {r["from_uid"] if r["to_uid"] == uid else r["to_uid"] for r in pending}
        exclude = friend_ids | pending_ids | {uid}
        results = sf.search_profiles(query, exclude_uids=exclude)
    return render(request, "social/friend_search.html", {"query": query, "results": results})


@firebase_login_required
@require_POST
def friend_request_send(request, target_uid):
    uid = request.firebase_user["uid"]
    if target_uid != uid:
        profile = get_profile(target_uid)
        if profile is not None:
            sf.send_friend_request(uid, target_uid)
            messages.success(request, f"Friend request sent to {_display_name(profile, target_uid)}.")

    query = request.POST.get("q", "")
    url = reverse("social:friend_search")
    if query:
        url = f"{url}?{urlencode({'q': query})}"
    return redirect(url)


@firebase_login_required
@require_POST
def friend_request_accept(request, request_id):
    uid = request.firebase_user["uid"]
    friend_request = sf.get_friend_request(request_id)
    if friend_request is None:
        raise Http404
    if friend_request["to_uid"] != uid:
        raise PermissionDenied
    sf.respond_to_request(request_id, sf.STATUS_ACCEPTED)
    messages.success(request, "You are now friends.")
    return redirect("social:friend_list")


@firebase_login_required
@require_POST
def friend_request_decline(request, request_id):
    uid = request.firebase_user["uid"]
    friend_request = sf.get_friend_request(request_id)
    if friend_request is None:
        raise Http404
    if friend_request["to_uid"] != uid:
        raise PermissionDenied
    sf.respond_to_request(request_id, sf.STATUS_DECLINED)
    return redirect("social:friend_list")


@firebase_login_required
def friend_list(request):
    uid = request.firebase_user["uid"]

    friends = [
        {"uid": fid, "display_name": _display_name(get_profile(fid), fid)} for fid in sf.friend_uids(uid)
    ]
    incoming = [
        {**r, "from_display_name": _display_name(get_profile(r["from_uid"]), r["from_uid"])}
        for r in sf.incoming_requests(uid)
    ]
    outgoing = [
        {**r, "to_display_name": _display_name(get_profile(r["to_uid"]), r["to_uid"])}
        for r in sf.outgoing_requests(uid)
    ]

    return render(
        request,
        "social/friend_list.html",
        {"friends": friends, "incoming": incoming, "outgoing": outgoing},
    )


@firebase_login_required
def friend_portfolio_view(request, target_uid):
    uid = request.firebase_user["uid"]
    if not sf.are_friends(uid, target_uid):
        raise PermissionDenied

    portfolio = get_or_create_portfolio(target_uid)
    display_name = _display_name(get_profile(target_uid), target_uid)
    return render(
        request,
        "portfolio/friend_detail.html",
        {"portfolio": portfolio, "friend_display_name": display_name},
    )
