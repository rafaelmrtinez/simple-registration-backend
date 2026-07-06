"""This module contains serializers for the registration app."""
from rest_framework import serializers
from registration.models import UserProfile


class UserProfileSerializer(serializers.Serializer):
    """Serializer for the UserProfile model."""
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField()
    mobile_number = serializers.CharField(max_length=11)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)

    def create(self, validated_data) -> UserProfile:
        return UserProfile.objects.create(**validated_data)

    def update(self, instance, validated_data) -> UserProfile:
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.date_of_birth = validated_data.get(
            'date_of_birth', instance.date_of_birth)
        instance.mobile_number = validated_data.get(
            'mobile_number', instance.mobile_number)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance
