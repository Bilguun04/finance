import json

import requests
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from firebase_admin import auth as firebase_auth

from .firebase import get_firebase_app

DEFAULT_PASSWORD = "correcthorsebattery9"


class FirestoreTestCase(TestCase):
    """Base test case that clears the Firebase emulator state before each test."""

    def setUp(self):
        super().setUp()
        get_firebase_app()
        self._clear_emulators()

    def _clear_emulators(self):
        project_id = settings.FIREBASE_PROJECT_ID
        if settings.FIRESTORE_EMULATOR_HOST:
            requests.delete(
                f"http://{settings.FIRESTORE_EMULATOR_HOST}"
                f"/emulator/v1/projects/{project_id}/databases/(default)/documents"
            )
        if settings.FIREBASE_AUTH_EMULATOR_HOST:
            requests.delete(
                f"http://{settings.FIREBASE_AUTH_EMULATOR_HOST}/emulator/v1/projects/{project_id}/accounts"
            )

    def create_user(self, email, password=DEFAULT_PASSWORD, display_name=None):
        kwargs = {"email": email, "password": password}
        if display_name:
            kwargs["display_name"] = display_name
        return firebase_auth.create_user(**kwargs)

    def get_id_token(self, email, password=DEFAULT_PASSWORD):
        resp = requests.post(
            f"http://{settings.FIREBASE_AUTH_EMULATOR_HOST}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
            params={"key": "fake-api-key"},
            json={"email": email, "password": password, "returnSecureToken": True},
        )
        resp.raise_for_status()
        return resp.json()["idToken"]

    def login(self, email, password=DEFAULT_PASSWORD):
        id_token = self.get_id_token(email, password)
        response = self.client.post(
            reverse("account:create_session"),
            data=json.dumps({"idToken": id_token}),
            content_type="application/json",
        )
        assert response.status_code == 200, response.content
        return response
