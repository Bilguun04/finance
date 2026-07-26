import threading

import firebase_admin
import google.auth.credentials
from django.conf import settings
from firebase_admin import credentials as firebase_credentials
from firebase_admin import auth as firebase_auth_module
from firebase_admin import firestore as firebase_firestore_module

_lock = threading.Lock()
_app = None


class _EmulatorGoogleCredential(google.auth.credentials.Credentials):
    """A no-op Google credential accepted by the Firebase emulator suite."""

    def refresh(self, request):
        self.token = "owner"


class _EmulatorCredentials(firebase_credentials.Base):
    def get_credential(self):
        return _EmulatorGoogleCredential()


def get_firebase_app():
    global _app
    if _app is not None:
        return _app
    with _lock:
        if _app is None:
            if settings.USE_FIREBASE_EMULATOR:
                cred = _EmulatorCredentials()
            elif settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH:
                cred = firebase_credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
            else:
                cred = firebase_credentials.ApplicationDefault()
            _app = firebase_admin.initialize_app(cred, options={"projectId": settings.FIREBASE_PROJECT_ID})
    return _app


def get_firestore_client():
    get_firebase_app()
    return firebase_firestore_module.client()


def get_firebase_auth():
    get_firebase_app()
    return firebase_auth_module
