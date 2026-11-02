from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import FriendRequest

User = get_user_model()


class FriendshipError(Exception):
    pass


def _between(a, b):
    return FriendRequest.objects.filter(Q(from_user=a, to_user=b) | Q(from_user=b, to_user=a))


def relationship(user, other):
    """How `user` relates to `other`: "self", "friends", "sent", "received" or None."""
    if user == other:
        return "self"
    request = _between(user, other).first()
    if request is None:
        return None
    if request.status == FriendRequest.Status.ACCEPTED:
        return "friends"
    return "sent" if request.from_user_id == user.id else "received"


def are_friends(a, b):
    return _between(a, b).filter(status=FriendRequest.Status.ACCEPTED).exists()


def friends_of(user):
    accepted = FriendRequest.Status.ACCEPTED
    return User.objects.filter(
        Q(sent_friend_requests__to_user=user, sent_friend_requests__status=accepted)
        | Q(received_friend_requests__from_user=user, received_friend_requests__status=accepted)
    ).distinct().order_by("username")


def friendship(user, other):
    return _between(user, other).filter(status=FriendRequest.Status.ACCEPTED).first()


def incoming_requests(user):
    return user.received_friend_requests.filter(status=FriendRequest.Status.PENDING).select_related("from_user")


def outgoing_requests(user):
    return user.sent_friend_requests.filter(status=FriendRequest.Status.PENDING).select_related("to_user")


def send_request(from_user, to_user):
    """Send a request, or accept theirs if `to_user` already asked `from_user`."""
    if from_user == to_user:
        raise FriendshipError("You can't add yourself as a friend.")

    with transaction.atomic():
        existing = _between(from_user, to_user).select_for_update().first()
        if existing is None:
            return FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        if existing.status == FriendRequest.Status.ACCEPTED:
            raise FriendshipError(f"You're already friends with {to_user.username}.")
        if existing.from_user_id == from_user.id:
            raise FriendshipError(f"You already sent {to_user.username} a request.")
        return _accept(existing)


def _accept(request):
    request.status = FriendRequest.Status.ACCEPTED
    request.responded_at = timezone.now()
    request.save(update_fields=["status", "responded_at"])
    return request


def _pending(request_id, **owner):
    try:
        return FriendRequest.objects.get(pk=request_id, status=FriendRequest.Status.PENDING, **owner)
    except FriendRequest.DoesNotExist:
        raise FriendshipError("That friend request no longer exists.")


def accept_request(user, request_id):
    return _accept(_pending(request_id, to_user=user))


def decline_request(user, request_id):
    _pending(request_id, to_user=user).delete()


def cancel_request(user, request_id):
    _pending(request_id, from_user=user).delete()


def unfriend(user, other):
    deleted, _ = _between(user, other).filter(status=FriendRequest.Status.ACCEPTED).delete()
    if not deleted:
        raise FriendshipError(f"You're not friends with {other.username}.")
