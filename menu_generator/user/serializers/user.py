from django.contrib.auth import get_user_model
from rest_framework import serializers
from user.models.profile import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ["settings"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "image",
            "date_create",
            "date_update",
            "profile",
        ]
        extra_kwargs = {"__all__": {"read_only": True}}
