from django.conf import settings


def firebase_user(request):
    return {
        "firebase_user": getattr(request, "firebase_user", None),
        "firebase_web_config": settings.FIREBASE_WEB_CONFIG,
        "firebase_auth_emulator_host": settings.FIREBASE_AUTH_EMULATOR_HOST,
    }
