from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError("Новый пароль не должен совпадать со старым.")
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Новые пароли не совпадают.")
        if len(attrs["new_password"]) < 8:
            raise serializers.ValidationError("Новый пароль должен быть не менее 8 символов.")
        if attrs["new_password"].isdigit() or attrs["new_password"].isalpha():
            raise serializers.ValidationError("Новый пароль должен содержать и буквы и цифры.")
        if attrs["new_password"].islower():
            raise serializers.ValidationError(
                "Новый пароль должен содержать хотя бы одну заглавную букву."
            )
        return attrs


class DeleteAccountSerializer(serializers.Serializer):
    user_pk = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)


class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "image"]
        extra_kwargs = {
            "username": {"required": False, "write_only": True},
            "image": {"required": False, "write_only": True},
        }

    def validate(self, attrs):
        if attrs.get("username"):
            if "admin" in attrs["username"]:
                raise serializers.ValidationError("Некорректное имя пользователя.")
            if User.objects.filter(username=attrs["username"]).exists():
                raise serializers.ValidationError("Пользователь с таким именем уже существует.")
            if len(attrs["username"]) < 6:
                raise serializers.ValidationError(
                    "Имя пользователя должно быть не менее 6 символов."
                )
        return attrs

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        image = validated_data.get("image")
        if image is None:
            image = "img/no_photo.png"
        instance.image = image
        instance.save()
        return instance
