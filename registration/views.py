"""This module contains the views for the registration app."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from registration.serializers import UserProfileSerializer, UserProfileListSerializer
from registration.models import UserProfile as UserProfileModel


class UserProfile(APIView):
    """
    List all user profiles, or create a new user profile.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Return all user profiles or filter by search query."""
        try:
            query = request.query_params.get("q", "").strip()
            profiles = UserProfileModel.objects.all()

            if query:
                profiles = self._search_profiles(query, profiles)

            serializer = UserProfileListSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _search_profiles(self, query: str, queryset):
        """Search profiles by id, name, mobile, or email."""
        from registration.utils import decode_id
        from django.db.models import Q

        # Try to decode as derived ID first
        if query.startswith("U-"):
            try:
                raw_id = decode_id(query)
                return queryset.filter(id=raw_id)
            except Exception:
                pass

        # Split query into parts for first name + last name search
        parts = query.split()
        if len(parts) == 2:
            first, last = parts[0], parts[1]
            return queryset.filter(
                Q(first_name__icontains=first) & Q(last_name__icontains=last)
            ).distinct()

        # Search by first name, last name, mobile, email
        return queryset.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(mobile_number__icontains=query) |
            Q(email__icontains=query)
        ).distinct()

    def post(self, request):
        """Create a new user profile."""
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
