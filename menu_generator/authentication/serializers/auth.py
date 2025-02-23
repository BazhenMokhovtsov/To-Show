from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    login_data = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        password = attrs["password"]

        if len(password) < 8:
            raise serializers.ValidationError("Пароль должен быть не менее 8 символов.")
        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError("Пароль должен содержать и буквы и цифры.")
        if password.islower():
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву."
            )
        for char in password:
            if char == " ":
                raise serializers.ValidationError("Пароль не должен содержать пробелы.")
            if not char.isdigit() and not char.isalpha():
                raise serializers.ValidationError("Пароль не должен иметь спецсимволы.")
        return attrs


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
