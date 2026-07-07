from unittest.mock import MagicMock, patch
from django.test import TestCase
from rest_framework.test import APIClient
from registration.serializers import UserProfileSerializer
from registration.utils import encode_id, decode_id
from registration.models import UserProfile as UserProfileModel

VALID_PAYLOAD = {
    "username": "jdoe",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "mobile_number": "09123456789",
    "email": "jdoe@example.com",
    "password": "securepass123",
}


class UserProfileViewTest(TestCase):
    """Test that the UserProfile view is reachable."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/user/register/"

    @patch("registration.serializers.UserProfile.objects.create")
    def test_post_returns_201_on_valid_data(self, mock_create):
        from registration.models import UserProfile as UP
        mock_instance = UP.__new__(UP)
        mock_instance.__dict__.update(VALID_PAYLOAD)
        mock_create.return_value = mock_instance
        response = self.client.post(self.url, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 201)

    def test_post_returns_400_on_invalid_data(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)


class UserProfileSerializerTest(TestCase):
    """Test that the serializer truly creates a UserProfile."""

    @patch("registration.serializers.UserProfile.objects.create")
    def test_create_returns_user_profile(self, mock_create):
        mock_instance = MagicMock()
        mock_create.return_value = mock_instance

        serializer = UserProfileSerializer(data=VALID_PAYLOAD)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        result = serializer.save()

        mock_create.assert_called_once_with(**serializer.validated_data)
        self.assertEqual(result, mock_instance)


class GetAllProfilesTest(TestCase):
    """Tests for GET /user/profiles/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/user/profiles/"

    @patch("registration.views.UserProfileModel.objects.all")
    def test_get_returns_200_with_profile_list(self, mock_all):
        """Happy path: returns 200 with serialized profiles."""
        from registration.models import UserProfile as UP
        from datetime import date, datetime, timezone

        mock_profile = UP.__new__(UP)
        mock_profile.__dict__.update({
            "id": 1,
            "username": "jdoe",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": date(1990, 1, 1),
            "mobile_number": "09123456789",
            "email": "jdoe@example.com",
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "entered_by_id": "admin",
        })
        mock_all.return_value = [mock_profile]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        profile = data[0]
        self.assertIn("id", profile)
        self.assertNotEqual(profile["id"], 1)  # must be derived, not raw
        self.assertEqual(profile["username"], "jdoe")
        self.assertEqual(profile["first_name"], "John")
        self.assertEqual(profile["last_name"], "Doe")
        self.assertEqual(profile["date_of_birth"], "1990-01-01")
        self.assertEqual(profile["mobile_number"], "09123456789")
        self.assertEqual(profile["email"], "jdoe@example.com")
        self.assertIn("created_at", profile)
        self.assertEqual(profile["entered_by"], "admin")
        # derived id must be reversible
        self.assertEqual(decode_id(profile["id"]), 1)

    @patch("registration.views.UserProfileModel.objects.all")
    def test_get_returns_empty_list_when_no_profiles(self, mock_all):
        """Sad path: no profiles in DB returns empty list."""
        mock_all.return_value = []
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("registration.views.UserProfileModel.objects.all", side_effect=Exception("DB error"))
    def test_get_returns_500_on_db_error(self, mock_all):
        """Sad path: DB failure returns 500."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 500)


class IdUtilityTest(TestCase):
    """Tests for the central ID encode/decode utility."""

    def test_encode_returns_string(self):
        self.assertIsInstance(encode_id(1), str)

    def test_encode_hides_raw_id(self):
        self.assertNotIn("1", encode_id(1).replace("=", "")[:3])

    def test_decode_reverses_encode(self):
        self.assertEqual(decode_id(encode_id(42)), 42)

    def test_decode_invalid_raises(self):
        with self.assertRaises(Exception):
            decode_id("not-valid!!")


class SearchProfilesTest(TestCase):
    """Tests for GET /user/profiles/?q=<query> endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/user/profiles/"
        from datetime import date

        # Create test profiles
        self.p1 = UserProfileModel.objects.create(
            username="jdoe1",
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
            mobile_number="09123456789",
            email="jdoe@example.com",
            password="pass123",
            entered_by_id="admin",
        )
        self.p2 = UserProfileModel.objects.create(
            username="asmith",
            first_name="Alice",
            last_name="Smith",
            date_of_birth=date(1985, 5, 15),
            mobile_number="09876543210",
            email="alice@example.com",
            password="pass456",
            entered_by_id="admin",
        )

    def test_search_by_first_name(self):
        response = self.client.get(f"{self.url}?q=John")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], "John")

    def test_search_by_last_name(self):
        response = self.client.get(f"{self.url}?q=Smith")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["last_name"], "Smith")

    def test_search_by_mobile_number(self):
        response = self.client.get(f"{self.url}?q=09123456789")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["mobile_number"], "09123456789")

    def test_search_by_email(self):
        response = self.client.get(f"{self.url}?q=alice@example.com")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["email"], "alice@example.com")

    def test_search_by_derived_id(self):
        derived_id = encode_id(self.p1.id)
        response = self.client.get(f"{self.url}?q={derived_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], derived_id)

    def test_search_first_name_last_name_combination(self):
        response = self.client.get(f"{self.url}?q=John+Doe")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], "John")
        self.assertEqual(data[0]["last_name"], "Doe")

    def test_search_no_results(self):
        response = self.client.get(f"{self.url}?q=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_search_partial_match(self):
        response = self.client.get(f"{self.url}?q=jo")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], "John")


class UserProfileModelTest(TestCase):
    """Test that UserProfile.objects.create saves to the database (mocked)."""

    @patch("registration.models.UserProfile.objects.create")
    def test_model_save_is_called_with_correct_data(self, mock_create):
        from registration.models import UserProfile

        mock_instance = MagicMock(spec=UserProfile)
        mock_create.return_value = mock_instance

        result = UserProfile.objects.create(**VALID_PAYLOAD)

        mock_create.assert_called_once_with(**VALID_PAYLOAD)
        self.assertEqual(result, mock_instance)
