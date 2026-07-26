from django.utils import timezone

from finance.firebase import get_firestore_client

PROFILES_COLLECTION = "profiles"


def _profile_ref(uid):
    return get_firestore_client().collection(PROFILES_COLLECTION).document(uid)


def get_profile(uid):
    snapshot = _profile_ref(uid).get()
    if not snapshot.exists:
        return None
    data = snapshot.to_dict()
    data["uid"] = uid
    return data


def create_profile_if_missing(uid, display_name="", email=""):
    ref = _profile_ref(uid)
    if ref.get().exists:
        return
    display_name_lower = display_name.strip().lower() if display_name else ""
    ref.set(
        {
            "display_name": display_name or "",
            "display_name_lower": display_name_lower,
            "email": email,
            "bio": "",
            "created_at": timezone.now().isoformat(),
        }
    )


def update_profile(uid, display_name, bio):
    _profile_ref(uid).set(
        {
            "display_name": display_name,
            "display_name_lower": display_name.strip().lower(),
            "bio": bio,
        },
        merge=True,
    )
