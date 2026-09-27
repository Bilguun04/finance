from .models import Profile


def get_profile(user_id):
    try:
        profile = Profile.objects.select_related("user").get(user_id=user_id)
    except Profile.DoesNotExist:
        return None
    return {
        "uid": profile.user_id,
        "display_name": profile.display_name,
        "email": profile.user.email,
        "bio": profile.bio,
    }


def create_profile_if_missing(user, display_name=""):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"display_name": display_name or user.get_username()},
    )
    return profile


def update_profile(user_id, display_name, bio):
    profile, _ = Profile.objects.get_or_create(user_id=user_id)
    profile.display_name = display_name
    profile.bio = bio
    profile.save(update_fields=["display_name", "bio"])
    return profile