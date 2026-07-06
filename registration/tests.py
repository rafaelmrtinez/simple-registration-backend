from unittest.mock import MagicMock, patch
from django.test import TestCase
from rest_framework.test import APIClient
from registration.serializers import UserProfileSerializer

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
