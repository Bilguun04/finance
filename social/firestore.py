from django.utils import timezone
from google.cloud.firestore_v1.base_query import FieldFilter

from finance.firebase import get_firestore_client

COLLECTION = "friend_requests"
PROFILES_COLLECTION = "profiles"

STATUS_PENDING = "PENDING"
STATUS_ACCEPTED = "ACCEPTED"
STATUS_DECLINED = "DECLINED"


def _collection():
    return get_firestore_client().collection(COLLECTION)


def _to_dict(doc):
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def get_friend_request(request_id):
    doc = _collection().document(request_id).get()
    if not doc.exists:
        return None
    return _to_dict(doc)


def find_existing_request(uid_a, uid_b):
    for direction in ((uid_a, uid_b), (uid_b, uid_a)):
        docs = list(
            _collection()
            .where(filter=FieldFilter("from_uid", "==", direction[0]))
            .where(filter=FieldFilter("to_uid", "==", direction[1]))
            .limit(1)
            .stream()
        )
        if docs:
            return _to_dict(docs[0])
    return None


def send_friend_request(from_uid, to_uid):
    if from_uid == to_uid or find_existing_request(from_uid, to_uid):
        return None
    ref = _collection().document()
    ref.set(
        {
            "from_uid": from_uid,
            "to_uid": to_uid,
            "status": STATUS_PENDING,
            "created_at": timezone.now().isoformat(),
            "responded_at": None,
        }
    )
    return _to_dict(ref.get())


def respond_to_request(request_id, status):
    _collection().document(request_id).set(
        {"status": status, "responded_at": timezone.now().isoformat()}, merge=True
    )


def incoming_requests(uid):
    docs = (
        _collection()
        .where(filter=FieldFilter("to_uid", "==", uid))
        .where(filter=FieldFilter("status", "==", STATUS_PENDING))
        .stream()
    )
    return [_to_dict(doc) for doc in docs]


def outgoing_requests(uid):
    docs = (
        _collection()
        .where(filter=FieldFilter("from_uid", "==", uid))
        .where(filter=FieldFilter("status", "==", STATUS_PENDING))
        .stream()
    )
    return [_to_dict(doc) for doc in docs]


def friend_uids(uid):
    from_docs = (
        _collection()
        .where(filter=FieldFilter("from_uid", "==", uid))
        .where(filter=FieldFilter("status", "==", STATUS_ACCEPTED))
        .stream()
    )
    to_docs = (
        _collection()
        .where(filter=FieldFilter("to_uid", "==", uid))
        .where(filter=FieldFilter("status", "==", STATUS_ACCEPTED))
        .stream()
    )
    uids = {doc.to_dict()["to_uid"] for doc in from_docs}
    uids |= {doc.to_dict()["from_uid"] for doc in to_docs}
    return uids


def are_friends(uid_a, uid_b):
    return uid_b in friend_uids(uid_a)


def search_profiles(prefix, exclude_uids=()):
    prefix_lower = prefix.strip().lower()
    if not prefix_lower:
        return []
    end = prefix_lower + ""
    docs = (
        get_firestore_client()
        .collection(PROFILES_COLLECTION)
        .where(filter=FieldFilter("display_name_lower", ">=", prefix_lower))
        .where(filter=FieldFilter("display_name_lower", "<=", end))
        .limit(20)
        .stream()
    )
    results = []
    for doc in docs:
        if doc.id in exclude_uids:
            continue
        data = doc.to_dict()
        results.append({"uid": doc.id, "display_name": data.get("display_name", ""), "email": data.get("email", "")})
    return results
