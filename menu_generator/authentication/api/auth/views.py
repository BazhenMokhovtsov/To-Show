from authentication.serializers.auth import *
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class Login(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Авторизация",
        description="""
            Эндпоинт для входа в систему. 
            Принимает данные пользователя и возвращает JWT токены. 
            Может быть осуществлен вход по логину или почте.
        """,
        tags=["token"],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response={"text": "text"},
                description="Успешная авторизация",
                examples=[
                    OpenApiExample(
                        "Пример ответа при успешной авторизации",
                        {"refresh": "refresh_token", "access": "access_token"},
                    )
                ],
            ),
            404: OpenApiResponse(
                response={"text": "text"},
                description="Неверный логин или пароль",
                examples=[
                    OpenApiExample(
                        "Пример ответа при неправильном логине или пароле",
                        {"detail": "Неверный логин или пароль."},
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
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        login_data = serializer.validated_data["login_data"]
        password = serializer.validated_data["password"]

        if "@" in login_data:
            login_user = User.objects.get(email=login_data)
            user = authenticate(username=login_user.username, password=password)
        else:
            user = authenticate(username=login_data, password=password)

        if not user:
            return Response(
                {"detail": "Неверный логин или пароль."},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = RefreshToken.for_user(user)
        token.payload.update(
            {
                "user_id": user.id,
            }
        )

        return Response(
            {
                "refresh": str(token),
                "access": str(token.access_token),
            },
            status=status.HTTP_200_OK,
        )


class Logout(generics.GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Выход из системы",
        description="""
        Эндпоинт для выхода из системы. Блокирует переданный refresh-токен.
        """,
        tags=["token"],
        request=RefreshTokenSerializer,
        responses={
            200: OpenApiResponse(
                response={"text": "text"},
                description="Токен успешно заблокирован.",
                examples=[
                    OpenApiExample(
                        "Пример ответа при успешном выходе",
                        {"detail": "Вы вышли из системы."},
                    ),
                ],
            ),
            400: OpenApiResponse(
                response={"text": "text"},
                description="Пример ответа неверных данных.",
                examples=[
                    OpenApiExample(
                        "Пример ответа неверно вверенных данных.",
                        {"detail": "Токен уже недействителен."},
                    )
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        token = request.data.get("refresh")
        try:
            refresh = RefreshToken(token)
            refresh.blacklist()
        except TokenError:
            return Response(
                {"detail": "Токен уже недействителен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Вы вышли из системы."}, status=status.HTTP_200_OK)


class Refresh(generics.GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Обновление access_token",
        description="""
        Эндпоинт для обновления access_token. 
        Требует передать действительный refresh-токен.
        """,
        tags=["token"],
        request=RefreshTokenSerializer,
        responses={
            200: OpenApiResponse(
                response={"text": "text"},
                description="Токен успешно обновлен.",
                examples=[
                    OpenApiExample(
                        "Пример ответа при верном refresh_token",
                        {"access": "access_token"},
                    ),
                ],
            ),
            400: OpenApiResponse(
                response={"text": "text"},
                description="Пример ответа неверных данных",
                examples=[
                    OpenApiExample(
                        "Пример ответа при неверном refresh_token.",
                        {"detail": "Токен уже недействителен."},
                    )
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        token = request.data.get("refresh")
        try:
            refresh = RefreshToken(token)
        except TokenError:
            return Response(
                {"detail": "Токен уже недействителен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"access": str(refresh.access_token)}, status=status.HTTP_200_OK)
