import datetime
import random

from authentication.serializers.another import *
from authentication.serializers.registration import CodeSeriazlizer
from celery import current_app
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

User = get_user_model()


# TODO: Убрать текущую затычку кода в ответе.
class RememberPasswordFirstStep(generics.GenericAPIView):
    serializer_class = RememberPasswordFirstStepSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Восстановление пароля первый шаг",
        description="""
        Эндпоинт для восстановления пароля. Проверяется логин пользователя, 
        после чего отправляется письмо с кодом подтверждения.
        """,
        tags=["remember_password"],
        request=RememberPasswordFirstStepSerializer,
        responses={
            200: OpenApiResponse(
                response={"text": "text"},
                description="Пример успешного ответа",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value={"detail": "Письмо отправлено, код 123456"},
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"text": "text"},
                description="Неправильные данные",
                examples=[
                    OpenApiExample(
                        "Пример ответа при неверном введенном логине",
                        {"detail": "Пользователь не найден"},
                    ),
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        login_data = serializer.validated_data["login_data"]
        try:
            if "@" in login_data:
                user = User.objects.get(email=login_data)
            else:
                user = User.objects.get(username=login_data)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        code = random.randint(100000, 999999)

        current_app.send_task(
            "send_mail_task",
            kwargs={
                "subject": "Восстановление пароля.",
                "message": f"Ваш код: {code}",
                "to_email": user.email,
            },
        )

        session = request.session
        session["user_data"] = {
            "user": user.pk,
            "code": code,
            "expired_at": datetime.datetime.now() + datetime.timedelta(minutes=5),
        }
        session.save()

        return Response({"detail": f"Письмо отправлено, код {code}"}, status=status.HTTP_200_OK)


class RemeberPasswordSecondStep(generics.GenericAPIView):
    serializer_class = CodeSeriazlizer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Восстановление пароля второй шаг",
        description="""
        Эндпоинт для восстановления пароля. Проверяется код подтверждения, 
        после чего отправляется сообщение верный он или не верный.
        """,
        tags=["remember_password"],
        request=CodeSeriazlizer,
        responses={
            200: OpenApiResponse(
                response={"text": "text"},
                description="Пример успешного ответа",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value={"detail": "Код верный"},
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"text": "text"},
                description="Неправильные данные",
                examples=[
                    OpenApiExample(
                        "Пример ответа при неверном введенном коде",
                        {"detail": "Неверный код"},
                    ),
                    OpenApiExample(
                        "Пример ответа при истекшем времени кода",
                        {"detail": "Срок действия кода истек"},
                    ),
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = request.session["user_data"]

        if int(user_data["code"]) != int(serializer.validated_data["code"]):
            return Response({"detail": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        if user_data["expired_at"] < datetime.datetime.now():
            return Response(
                {"detail": "Срок действия кода истек"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Код верный"}, status=status.HTTP_200_OK)


class RememberPasswordSetPassword(generics.GenericAPIView):
    serializer_class = PasswordSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Восстановление пароля третий шаг",
        description="""
        Эндпоинт для восстановления пароля третий шаг. Происходит установка пароля.
        Если пароль введен верно, выводится сообщение о успешной смене пароля.
        """,
        tags=["remember_password"],
        request=PasswordSerializer,
        responses={
            200: OpenApiResponse(
                response={"text": "text"},
                description="Пример успешного ответа",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value={"detail": "Пользователь успешно изменил пароль"},
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"text": "text"},
                description="Неправильные данные пароля",
                examples=[
                    OpenApiExample(
                        "Пример ответа при неверном введенном пароле (Меньше 8 символов)",
                        {"non_field_errors": "Пароль должен быть не менее 8 символов."},
                    ),
                    OpenApiExample(
                        "Пример ответа при неверном введенном пароле (Все прописными)",
                        {
                            "non_field_errors": "Пароль должен содержать хотя бы одну заглавную букву."
                        },
                    ),
                    OpenApiExample(
                        "Пример ответа при неверном введенном пароле (Нет цифр или букв)",
                        {"non_field_errors": "Пароль должен содержать и буквы и цифры."},
                    ),
                    OpenApiExample(
                        "Пример ответа при неверном введенном пароле (Содержит пробел)",
                        {"non_field_errors": "Пароль не должен содержать пробелы."},
                    ),
                    OpenApiExample(
                        "Пример ответа при неверном введенном пароле (Содержит спецсимволы)",
                        {"non_field_errors": "Пароль не должен иметь спецсимволы"},
                    ),
                    OpenApiExample(
                        "Пример ответа при неверном введенном пароле (Пароли не совпадают)",
                        {"non_field_errors": "Пароли не совпадают"},
                    ),
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(pk=request.session["user_data"]["user"])
        user.set_password(serializer.validated_data["password"])
        user.save()

        del request.session["user_data"]

        return Response(
            {"detail": "Пользователь успешно изменил пароль"}, status=status.HTTP_200_OK
        )
