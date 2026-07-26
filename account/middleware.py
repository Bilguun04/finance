from firebase_admin import auth as firebase_auth

from finance.firebase import get_firebase_app

SESSION_COOKIE_NAME = "fb_session"


class FirebaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        get_firebase_app()
        request.firebase_user = self._authenticate(request)
        return self.get_response(request)

    def _authenticate(self, request):
        cookie = request.COOKIES.get(SESSION_COOKIE_NAME)
        if not cookie:
            return None
        try:
            decoded = firebase_auth.verify_session_cookie(cookie, check_revoked=True)
        except (firebase_auth.InvalidSessionCookieError, ValueError):
            return None
        return {
            "uid": decoded["uid"],
            "email": decoded.get("email", ""),
            "display_name": decoded.get("name", ""),
        }
