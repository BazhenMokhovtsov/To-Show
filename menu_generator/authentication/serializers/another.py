from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RememberPasswordFirstStepSerializer(serializers.Serializer):
    login_data = serializers.CharField(required=True)


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        password = attrs["password"]
        confirm_password = attrs["confirm_password"]

        if len(password) < 8:
            raise serializers.ValidationError("Пароль должен быть не менее 8 символов.")
        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError("Пароль должен содержать и буквы и цифры.")
        if password.islower():
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву."
            )
        if password != confirm_password:
            raise serializers.ValidationError("Пароли не совпадают.")
        for char in password:
            if char == " ":
                raise serializers.ValidationError("Пароль не должен содержать пробелы.")
            if not char.isdigit() and not char.isalpha():
                raise serializers.ValidationError("Пароль не должен иметь спецсимволы")
        return attrs
