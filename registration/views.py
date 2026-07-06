"""This module contains the views for the registration app."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from registration.serializers import UserProfileSerializer


class UserProfile(APIView):
    """
    List all user profiles, or create a new user profile.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Create a new user profile."""
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
