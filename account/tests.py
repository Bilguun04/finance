import re
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.shortcuts import resolve_url
from django.test import Client, override_settings
from django.urls import reverse

from finance.testing import DEFAULT_PASSWORD, FinanceTestCase

User = get_user_model()

PASSWORD = DEFAULT_PASSWORD
NEW_PASSWORD = "NewSecurePassword456!"

RESET_URL_PATTERN = re.compile(r"https?://\S+/reset/\S+")


def session_user_id(client):
    return client.session.get("_auth_user_id")


class LoginTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.login_url = reverse("account:login")

    def login_data(self, username=None, password=PASSWORD, **extra):
        return {
            "username": username or self.user.get_username(),
            "password": password,
            **extra,
        }

    # Login: Valid credentials accepted
    def test_login_valid_credentials(self):
        response = self.client.post(self.login_url, self.login_data())

        self.assertRedirects(
            response,
            resolve_url(settings.LOGIN_REDIRECT_URL),
            fetch_redirect_response=False,
        )
        self.assertEqual(session_user_id(self.client), str(self.user.pk))

    # Login: Invalid password rejected
    def test_login_invalid_password(self):
        response = self.client.post(
            self.login_url, self.login_data(password="wrong-password")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(session_user_id(self.client))
        self.assertTrue(response.context["form"].non_field_errors())

    # Login: Nonexistent user rejected
    def test_login_nonexistent_user(self):
        response = self.client.post(
            self.login_url, self.login_data(username="nonexistent")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(session_user_id(self.client))
        self.assertTrue(response.context["form"].errors)

    # Login: Inactive user rejected (even with the correct password)
    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(self.login_url, self.login_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(session_user_id(self.client))

    # Login: Authenticated user redirected away from the login page
    def test_login_authenticated_user_redirected(self):
        self.client.force_login(self.user)

        response = self.client.get(self.login_url)

        self.assertRedirects(
            response,
            resolve_url(settings.LOGIN_REDIRECT_URL),
            fetch_redirect_response=False,
        )

    # Login: Safe "next" URL is honoured
    def test_login_safe_next_honoured(self):
        next_url = reverse("account:profile")

        response = self.client.post(
            self.login_url, self.login_data(next=next_url)
        )

        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    # Security: Open redirect prevented
    def test_open_redirect_prevented(self):
        response = self.client.post(
            self.login_url,
            self.login_data(next="https://evil.example.com"),
        )

        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(urlparse(response.url).netloc, "evil.example.com")
        self.assertEqual(response.url, resolve_url(settings.LOGIN_REDIRECT_URL))
        self.assertEqual(session_user_id(self.client), str(self.user.pk))

    # Security: CSRF protection enforced
    def test_csrf_protection_enforced(self):
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(self.login_url, self.login_data())

        self.assertEqual(response.status_code, 403)
        self.assertIsNone(session_user_id(csrf_client))


class LogoutTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    # Logout: Session cleared
    def test_logout_session_cleared(self):
        response = self.client.post(reverse("account:logout"))

        self.assertRedirects(
            response,
            resolve_url(settings.LOGOUT_REDIRECT_URL),
            fetch_redirect_response=False,
        )
        self.assertIsNone(session_user_id(self.client))

    # Logout: Protected pages inaccessible afterward
    def test_logout_protected_pages_inaccessible(self):
        self.client.post(reverse("account:logout"))

        response = self.client.get(reverse("account:profile"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.url).path, reverse("account:login"))

    # Logout: GET is not allowed (prevents logout via a link/image on another site)
    def test_logout_requires_post(self):
        response = self.client.get(reverse("account:logout"))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(session_user_id(self.client), str(self.user.pk))


class RegisterTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.register_url = reverse("account:register")

    def registration_data(
        self,
        username="bob",
        email="bob@example.com",
        password=PASSWORD,
        password_confirmation=None,
    ):
        return {
            "username": username,
            "email": email,
            "password1": password,
            "password2": password_confirmation or password,
        }

    def assert_rejected(self, response, field=None):
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        if field:
            self.assertIn(field, form.errors)
        else:
            self.assertTrue(form.errors)

    # Registration: Valid user registration (and user is logged in)
    def test_registration_valid_user(self):
        response = self.client.post(self.register_url, self.registration_data())

        self.assertRedirects(
            response,
            resolve_url(settings.LOGIN_REDIRECT_URL),
            fetch_redirect_response=False,
        )
        user = User.objects.get(username="bob")
        self.assertEqual(user.email, "bob@example.com")
        self.assertEqual(session_user_id(self.client), str(user.pk))

    # Registration: Password stored as a hash
    def test_registration_password_stored_as_hash(self):
        self.client.post(self.register_url, self.registration_data())

        user = User.objects.get(username="bob")
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))

    # Registration: Duplicate username rejected (case-insensitive)
    def test_registration_duplicate_username(self):
        User.objects.create_user(
            username="bob", email="original@example.com", password=PASSWORD
        )

        for username in ("bob", "BOB"):
            with self.subTest(username=username):
                response = self.client.post(
                    self.register_url,
                    self.registration_data(
                        username=username, email="another@example.com"
                    ),
                )

                self.assert_rejected(response, "username")
                self.assertEqual(
                    User.objects.filter(username__iexact="bob").count(), 1
                )

    # Registration: Duplicate email rejected (case-insensitive)
    def test_registration_duplicate_email(self):
        User.objects.create_user(
            username="original", email="bob@example.com", password=PASSWORD
        )

        for email in ("bob@example.com", "Bob@Example.COM"):
            with self.subTest(email=email):
                response = self.client.post(
                    self.register_url,
                    self.registration_data(email=email),
                )

                self.assert_rejected(response, "email")
                self.assertFalse(User.objects.filter(username="bob").exists())

    # Registration: Email is required
    def test_registration_email_required(self):
        response = self.client.post(
            self.register_url, self.registration_data(email="")
        )

        self.assert_rejected(response, "email")
        self.assertFalse(User.objects.filter(username="bob").exists())

    # Registration: Invalid email rejected
    def test_registration_invalid_email(self):
        response = self.client.post(
            self.register_url, self.registration_data(email="not-an-email")
        )

        self.assert_rejected(response, "email")
        self.assertFalse(User.objects.filter(username="bob").exists())

    # Registration: Password validation enforced
    def test_registration_password_validation(self):
        for password in ("123", "password", "bob@example.com"):
            with self.subTest(password=password):
                response = self.client.post(
                    self.register_url,
                    self.registration_data(password=password),
                )

                self.assert_rejected(response, "password2")
                self.assertFalse(User.objects.filter(username="bob").exists())

    # Registration: Password confirmation must match
    def test_registration_password_mismatch(self):
        response = self.client.post(
            self.register_url,
            self.registration_data(password_confirmation=NEW_PASSWORD),
        )

        self.assert_rejected(response, "password2")
        self.assertFalse(User.objects.filter(username="bob").exists())

    # Registration: Authenticated user redirected away from the signup page
    def test_registration_authenticated_user_redirected(self):
        self.client.force_login(self.user)

        response = self.client.get(self.register_url)

        self.assertRedirects(
            response,
            resolve_url(settings.LOGIN_REDIRECT_URL),
            fetch_redirect_response=False,
        )


class SessionTests(FinanceTestCase):
    # Sessions: Anonymous users redirected to login (with "next")
    def test_anonymous_users_redirected_to_login(self):
        profile_url = reverse("account:profile")

        response = self.client.get(profile_url)

        self.assertRedirects(
            response,
            f"{reverse('account:login')}?next={profile_url}",
            fetch_redirect_response=False,
        )

    # Sessions: Authenticated users access protected pages
    def test_authenticated_users_access_protected_pages(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("account:profile"))

        self.assertEqual(response.status_code, 200)

    # Sessions: Session persists between requests
    def test_session_persists_between_requests(self):
        self.client.post(
            reverse("account:login"),
            {"username": self.user.get_username(), "password": PASSWORD},
        )

        for _ in range(2):
            response = self.client.get(reverse("account:profile"))
            self.assertEqual(response.status_code, 200)

        self.assertEqual(session_user_id(self.client), str(self.user.pk))


class ProfileTests(FinanceTestCase):
    # Profile: Shows the logged-in user's account details
    def test_profile_shows_user_details(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("account:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.get_username())
        self.assertContains(response, self.user.email)


class PasswordChangeTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.change_url = reverse("account:password_change")

    def change_data(self, old_password=PASSWORD, new_password=NEW_PASSWORD):
        return {
            "old_password": old_password,
            "new_password1": new_password,
            "new_password2": new_password,
        }

    # Password: Anonymous users cannot reach password change
    def test_password_change_requires_login(self):
        response = self.client.get(self.change_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.url).path, reverse("account:login"))

    # Password: Password change succeeds and keeps the user logged in
    def test_password_change_succeeds(self):
        self.client.force_login(self.user)

        response = self.client.post(self.change_url, self.change_data())

        self.assertRedirects(
            response,
            reverse("account:password_change_done"),
            fetch_redirect_response=False,
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(PASSWORD))

        response = self.client.get(reverse("account:profile"))
        self.assertEqual(response.status_code, 200)

    # Password: Incorrect old password rejected
    def test_incorrect_old_password_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.change_url, self.change_data(old_password="wrong-password")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("old_password", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    # Password: New password must pass validation
    def test_weak_new_password_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.change_url, self.change_data(new_password="123")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("new_password2", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTests(FinanceTestCase):
    def request_reset(self, email):
        return self.client.post(reverse("account:password_reset"), {"email": email})

    def reset_url_from_email(self):
        self.assertEqual(len(mail.outbox), 1)
        match = RESET_URL_PATTERN.search(mail.outbox[0].body)
        self.assertIsNotNone(match, "No reset link found in the email body")
        return match.group(0)

    # Password: Password reset flow succeeds
    def test_password_reset_flow_succeeds(self):
        response = self.request_reset(self.user.email)

        self.assertRedirects(
            response,
            reverse("account:password_reset_done"),
            fetch_redirect_response=False,
        )
        self.assertEqual(mail.outbox[0].to, [self.user.email])

        # The confirm view swaps the token for a session value and
        # redirects to a ".../set-password/" URL.
        response = self.client.get(self.reset_url_from_email())
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            response.url,
            {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
        )

        self.assertRedirects(
            response,
            reverse("account:password_reset_complete"),
            fetch_redirect_response=False,
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(PASSWORD))

    # Password: Reset invalidates sessions that were logged in before
    def test_password_reset_invalidates_existing_sessions(self):
        other_device = Client()
        other_device.force_login(self.user)

        self.request_reset(self.user.email)
        response = self.client.get(self.reset_url_from_email())
        self.client.post(
            response.url,
            {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
        )

        response = other_device.get(reverse("account:profile"))
        self.assertEqual(response.status_code, 302)

    # Password: Reset link can only be used once
    def test_password_reset_link_single_use(self):
        self.request_reset(self.user.email)
        reset_url = self.reset_url_from_email()

        response = self.client.get(reset_url)
        self.client.post(
            response.url,
            {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
        )

        response = Client().get(reset_url, follow=True)
        self.assertFalse(response.context["validlink"])

    # Password: Tampered reset token rejected
    def test_password_reset_invalid_token_rejected(self):
        self.request_reset(self.user.email)
        tampered_url = self.reset_url_from_email().rstrip("/") + "x/"

        response = self.client.get(tampered_url, follow=True)

        self.assertFalse(response.context["validlink"])

    # Security: Unknown email does not reveal whether an account exists
    def test_password_reset_unknown_email(self):
        response = self.request_reset("nobody@example.com")

        self.assertRedirects(
            response,
            reverse("account:password_reset_done"),
            fetch_redirect_response=False,
        )
        self.assertEqual(len(mail.outbox), 0)
