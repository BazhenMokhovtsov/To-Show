from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegistrationFirstStepSeriazlizer(serializers.Serializer):
    username = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        # Проверяем пароль
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают.")
        if len(data["password"]) < 8:
            raise serializers.ValidationError("Пароль должен быть не менее 8 символов.")
        if data["password"].isdigit() or data["password"].isalpha():
            raise serializers.ValidationError("Пароль должен состоять только из букв и цифр.")
        if data["password"].islower():
            raise serializers.ValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву."
            )
        for char in data["password"]:
            if char == " ":
                raise serializers.ValidationError("Пароль не должен содержать пробелы.")
            if not char.isdigit() and not char.isalpha():
                raise serializers.ValidationError("Пароль не должен иметь спецсимволы")
        # Проверяем имя пользователя
        try:
            User.objects.get(username=data["username"])
            raise serializers.ValidationError("Имя пользователя уже занято.")
        except User.DoesNotExist:
            if len(data["username"]) < 6:
                raise serializers.ValidationError(
                    "Имя пользователя должно быть не менее 6 символов."
                )
            pass
        # Проверяем почту
        try:
            User.objects.get(email=data["email"])
            raise serializers.ValidationError("Почта уже занята.")
        except User.DoesNotExist:
            pass
        return data


class CodeSeriazlizer(serializers.Serializer):
    code = serializers.IntegerField(required=True, write_only=True)
