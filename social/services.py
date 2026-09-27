from django.db.models import Q
from django.utils import timezone

from account.models import Profile

from .models import FriendRequest

STATUS_PENDING = FriendRequest.PENDING
STATUS_ACCEPTED = FriendRequest.ACCEPTED
STATUS_DECLINED = FriendRequest.DECLINED


def _to_dict(friend_request):
    return {
        "id": str(friend_request.id),
        "from_uid": friend_request.from_user_id,
        "to_uid": friend_request.to_user_id,
        "status": friend_request.status,
        "created_at": friend_request.created_at,
        "responded_at": friend_request.responded_at,
    }


def get_friend_request(request_id):
    try:
        return _to_dict(FriendRequest.objects.get(id=request_id))
    except FriendRequest.DoesNotExist:
        return None


def find_existing_request(uid_a, uid_b):
    friend_request = FriendRequest.objects.filter(
        Q(from_user_id=uid_a, to_user_id=uid_b) | Q(from_user_id=uid_b, to_user_id=uid_a)
    ).first()
    return _to_dict(friend_request) if friend_request else None


def send_friend_request(from_uid, to_uid):
    if from_uid == to_uid or find_existing_request(from_uid, to_uid):
        return None
    friend_request = FriendRequest.objects.create(from_user_id=from_uid, to_user_id=to_uid)
    return _to_dict(friend_request)


def respond_to_request(request_id, status):
    FriendRequest.objects.filter(id=request_id).update(status=status, responded_at=timezone.now())


def incoming_requests(uid):
    return [_to_dict(item) for item in FriendRequest.objects.filter(to_user_id=uid, status=STATUS_PENDING)]


def outgoing_requests(uid):
    return [_to_dict(item) for item in FriendRequest.objects.filter(from_user_id=uid, status=STATUS_PENDING)]


def friend_uids(uid):
    accepted = FriendRequest.objects.filter(
        Q(from_user_id=uid) | Q(to_user_id=uid), status=STATUS_ACCEPTED
    ).values_list("from_user_id", "to_user_id")
    return {to_id if from_id == uid else from_id for from_id, to_id in accepted}


def are_friends(uid_a, uid_b):
    return uid_b in friend_uids(uid_a)


def search_profiles(prefix, exclude_uids=()):
    prefix_lower = prefix.strip().lower()
    if not prefix_lower:
        return []
    profiles = Profile.objects.select_related("user").filter(
        display_name__istartswith=prefix_lower
    ).exclude(user_id__in=exclude_uids)[:20]
    return [
        {"uid": profile.user_id, "display_name": profile.display_name, "email": profile.user.email}
        for profile in profiles
    ]