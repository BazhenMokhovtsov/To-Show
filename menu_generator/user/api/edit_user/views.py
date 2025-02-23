import datetime
import random

from authentication.serializers.another import *
from authentication.serializers.registration import *
from celery import current_app
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from user.serializers.edit_user import *

User = get_user_model()


class ChangeEmailFirstStep(generics.GenericAPIView):
    serializer_class = EmailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        code = random.randrange(100000, 999999)

        # current_app.send_task(
        #     'send_mail_task',
        #     kwargs={
        #         'subject': 'Изменение почты',
        #         'message': f'Ваш код: {code}',
        #         'to_email': user.email
        #     }
        # )

        session = request.session
        session["change_email"] = {
            "user": user.pk,
            "email": serializer.validated_data["email"],
            "code": code,
            "expired_at": datetime.datetime.now() + datetime.timedelta(minutes=5),
        }
        session.save()

        return Response({"detail": f"Письмо отправлено. Код {code}"}, status=status.HTTP_200_OK)


class ChangeEmailSecondStep(generics.GenericAPIView):
    serializer_class = CodeSeriazlizer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = request.session["change_email"]

        if int(user_data["code"]) != int(serializer.validated_data["code"]):
            return Response({"detail": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        if user_data["expired_at"] < datetime.datetime.now():
            return Response(
                {"detail": "Срок действия кода истек"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if user.pk != user_data["user"]:
            return Response({"detail": "Ошибка пользователя."}, status=status.HTTP_404_NOT_FOUND)

        user.email = user_data["email"]
        user.save()

        del request.session["change_email"]

        return Response({"detail": "Почта успешно изменена."}, status=status.HTTP_200_OK)


class ChangePassword(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"detail": "Пароль успешно изменен."}, status=status.HTTP_200_OK)


class DeleteAccount(generics.GenericAPIView):
    serializer_class = DeleteAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user.delete()

        return Response({"detail": "Аккаунт успешно удален."}, status=status.HTTP_200_OK)


class EditUser(generics.GenericAPIView):
    serializer_class = EditUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.update(request.user, serializer.validated_data)

        return Response(
            {"detail": "Данные пользователя успешно изменены."},
            status=status.HTTP_200_OK,
        )
