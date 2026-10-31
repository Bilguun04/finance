from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import services
from .services import FriendshipError

User = get_user_model()

FRIENDS_URL = "social:friends"


def _back_to_friends(request):
    """Return to the friends page, keeping the search the action was made from."""
    query = request.POST.get("q", "").strip()
    url = reverse(FRIENDS_URL)
    return redirect(f"{url}?{urlencode({'q': query})}" if query else url)


@login_required
def friends(request):
    query = request.GET.get("q", "").strip()
    match = None
    if query:
        # Exact (case-insensitive) match only, so nobody can browse the user list by typing partial names.
        match = User.objects.filter(username__iexact=query).first()

    # distinct=True: friends_of() joins the request tables, which would otherwise multiply the count.
    friend_list = services.friends_of(request.user).annotate(
        shared_count=Count("portfolios", filter=Q(portfolios__is_public=True), distinct=True),
    )

    context = {
        "query": query,
        "match": match,
        "match_relationship": services.relationship(request.user, match) if match else None,
        "incoming": services.incoming_requests(request.user),
        "outgoing": services.outgoing_requests(request.user),
        "friends": friend_list,
    }
    return render(request, "social/friends.html", context)


@login_required
@require_POST
def send_request(request):
    to_user = get_object_or_404(User, username=request.POST.get("username", ""))
    try:
        friend_request = services.send_request(request.user, to_user)
    except FriendshipError as exc:
        messages.error(request, str(exc))
    else:
        if friend_request.status == friend_request.Status.ACCEPTED:
            messages.success(request, f"{to_user.username} had already asked you. You're now friends!")
        else:
            messages.success(request, f"Friend request sent to {to_user.username}.")
    return _back_to_friends(request)


def _request_action(action, success_message):
    @login_required
    @require_POST
    def view(request, request_id):
        try:
            action(request.user, request_id)
        except FriendshipError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, success_message)
        return _back_to_friends(request)
    return view


accept_request = _request_action(services.accept_request, "Friend request accepted.")
decline_request = _request_action(services.decline_request, "Friend request declined.")
cancel_request = _request_action(services.cancel_request, "Friend request cancelled.")


@login_required
@require_POST
def unfriend(request, username):
    other = get_object_or_404(User, username=username)
    try:
        services.unfriend(request.user, other)
    except FriendshipError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"You're no longer friends with {other.username}.")
    return redirect(FRIENDS_URL)


@login_required
def friend_profile(request, username):
    friend = get_object_or_404(User, username=username)
    friendship = services.friendship(request.user, friend)
    if friendship is None:
        # 404 rather than 403 so non-friends can't tell what's behind the page.
        raise Http404

    shared = [
        {"portfolio": portfolio, **portfolio.allocation()}
        for portfolio in friend.portfolios.filter(is_public=True).order_by("created_at")
    ]
    context = {"friend": friend, "friends_since": friendship.responded_at, "shared": shared}
    return render(request, "social/friend_profile.html", context)
