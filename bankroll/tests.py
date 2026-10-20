from django.test import TestCase
from .forms import SessionForm
from .models import Session

# Create your tests here.

class SessionFormTestCase(TestCase):
    def test_session_can_be_saved_to_database(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            'type': 'poker',
            'stakes': '2/5',
            'session_start': '2024-01-01 12:00:00',
            'session_end': '2024-01-01 14:00:00',
            'buyin': 50,
            'buyout': 150,
        }
        form = SessionForm(data=form_data)

        self.assertTrue(form.is_valid())
        session = form.save()

        saved_session = Session.objects.get(pk=session.pk)
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(saved_session.host, 'John Doe')
        self.assertEqual(saved_session.format, 'homegame')
        self.assertEqual(saved_session.buyin, 50)
        self.assertEqual(saved_session.buyout, 150)

    def test_session_modification(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            'type': 'poker',
            'stakes': '1/2',
            'session_start': '2024-01-01 12:00:00',
            'session_end': '2024-01-01 14:00:00',
            'buyin': 50,
            'buyout': 150,
        }
        form = SessionForm(data=form_data)

        self.assertTrue(form.is_valid())
        session = form.save()

        # Modify the session
        session.host = 'Jane Smith'
        session.format = 'casino'
        session.buyin = 75
        session.buyout = 225
        session.save()

        # Check that the changes were saved
        saved_session = Session.objects.get(pk=session.pk)
        self.assertEqual(saved_session.host, 'Jane Smith')
        self.assertEqual(saved_session.format, 'casino')
        self.assertEqual(saved_session.buyin, 75)
        self.assertEqual(saved_session.buyout, 225)

    def test_session_deletion(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            'type': 'poker',
            'stakes': '2/5',
            'session_start': '2024-01-01 12:00:00',
            'session_end': '2024-01-01 14:00:00',
            'buyin': 50,
            'buyout': 150,
        }
        form = SessionForm(data=form_data)

        self.assertTrue(form.is_valid())
        session = form.save()

        self.assertEqual(Session.objects.count(), 1)

        # Delete the session
        session.delete()

        # Check that the session was deleted
        self.assertEqual(Session.objects.count(), 0)

    def test_session_form_valid(self):
        form_data = {
            'host': 'John Doe',
            'format': 'casino',
            'type': 'poker',
            'stakes': '1/2',
            'session_start': '2024-01-01 12:00:00',
            'session_end': '2024-01-01 14:00:00',
            'buyin': 50,
            'buyout': 150,
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_session_form_invalid(self):
        form_data = {
            'host': '',
            'format': '',
            'type': '',
            'stakes': -100,
            'session_start': '',
            'session_end': '',
            'buyin': -50,
            'buyout': -150,
        }
        form = SessionForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_session_form_missing_required_fields(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            # Missing 'type', 'stakes', 'session_start', 'session_end', 'buyin', 'buyout'
        }
        form = SessionForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_session_form_invalid_date_format(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            'type': 'poker',
            'stakes': '2/5',
            'session_start': 'invalid-date-format',
            'session_end': '2024-01-01 14:00:00',
            'buyin': 50,
            'buyout': 150,
        }
        form = SessionForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_session_form_negative_buyin_buyout(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            'type': 'poker',
            'stakes': '1/2',
            'session_start': '2024-01-01 12:00:00',
            'session_end': '2024-01-01 14:00:00',
            'buyin': -50,
            'buyout': -150,
        }
        form = SessionForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_session_form_valid_with_optional_fields(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            'type': 'poker',
            'stakes': '1/2',
            'session_start': '2024-01-01 12:00:00',
            'session_end': '2024-01-01 14:00:00',
            'buyin': 50,
            'buyout': 150,
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_session_form_valid_with_blank_optional_fields(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            'type': '',
            'stakes': '1/2',
            'session_start': '2024-01-01 12:00:00',
            'session_end': '2024-01-01 14:00:00',
            'buyin': 50,
            'buyout': 150,
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_session_form_valid_with_null_optional_fields(self):
        form_data = {
            'host': 'John Doe',
            'format': 'homegame',
            'type': None,
            'stakes': '1/2',
            'session_start': '2024-01-01 12:00:00',
            'session_end': '2024-01-01 14:00:00',
            'buyin': 50,
            'buyout': 150,
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())