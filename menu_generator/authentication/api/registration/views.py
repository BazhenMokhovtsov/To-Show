import datetime
import random

from authentication.serializers.registration import *
from authentication.tasks import *
from celery import current_app
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

User = get_user_model()


# TODO: Убрать текущую затычку кода в ответе.
class RegistrationFirstStep(generics.GenericAPIView):
    serializer_class = RegistrationFirstStepSeriazlizer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Регистрация заполнение полей",
        description="""
        Эндпоинт для первого шага регистрации. Заполняются все поля, происходит проверка
        на доступность вводимых данных. Если все введено верно, отправляется письмо на 
        указанную почту с кодом подтверждения.
        """,
        tags=["registration"],
        request=RegistrationFirstStepSeriazlizer,
        responses={
            200: OpenApiResponse(
                response={"text": "text"},
                description="Пример успешного ответа",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value={"detail": "Письмо отправлено. Код 123456"},
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
                        "Пример ответа при неверном введенном имени пользователя",
                        {"non_field_errors": "Имя пользователя уже занято"},
                    ),
                    OpenApiExample(
                        "Пример ответа при неверном введенной почте",
                        {"non_field_errors": "Почта уже занята"},
                    ),
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        code = random.randint(100000, 999999)

        session = request.session
        session["user_data"] = {
            "username": data["username"],
            "email": data["email"],
            "password": data["password"],
            "code": code,
            "expired_at": datetime.datetime.now() + datetime.timedelta(minutes=5),
        }
        session.save()

        current_app.send_task(
            "send_mail_task",
            kwargs={
                "subject": "Регистрация",
                "message": f"Для подтверждения почты введите: {code}",
                "to_email": data["email"],
            },
        )

        return Response({"detail": f"Письмо отправлено. Код {code}"}, status=status.HTTP_200_OK)


class RegistrationSecondStep(generics.GenericAPIView):
    serializer_class = CodeSeriazlizer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Регистрация второй шаг",
        description="""
        Эндпоинт для второго шага регистрации. Проверяется код подтверждения, 
        после чего создается новый пользователь.
        """,
        tags=["registration"],
        request=CodeSeriazlizer,
        responses={
            200: OpenApiResponse(
                response={"text": "text"},
                description="Пример успешного ответа",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value={"detail": "Регистрация прошла успешно"},
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"text": "text"},
                description="Неправильные данные кода",
                examples=[
                    OpenApiExample(
                        "Пример ответа при неверном введенном коде (Срок действия истек)",
                        {"detail": "Срок действия кода истек"},
                    ),
                    OpenApiExample(
                        "Пример ответа при неверном введенном коде (Неверный код)",
                        {"detail": "Неверный код"},
                    ),
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = request.session["user_data"]

        if user_data["expired_at"] < datetime.datetime.now():
            return Response(
                {"detail": "Срок действия кода истек"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if int(user_data["code"]) != int(serializer.validated_data["code"]):
            return Response({"detail": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
        )

        del request.session["user_data"]

        return Response({"detail": "Регистрация прошла успешно"}, status=status.HTTP_200_OK)
