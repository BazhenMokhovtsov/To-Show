import os

import redis
from django.contrib.auth import get_user_model
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from recipes.custom_filters.filters import AllOpenRecipesFilter
from recipes.models.like import Like
from recipes.models.open_recipe import OpenRecipe
from recipes.serializers.open_recipe import *
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

User = get_user_model()


@extend_schema(
    description="""
        Эндпоинт возвращает список открытых рецептов. Доступна сортировка по рейтингу и дате создания. 
        Поиск по ключевым словам.
        Фильтрация.
    """,
    summary="Получение списка всех открытых рецептов с возможностью фильтрации и поиска",
    parameters=[
        OpenApiParameter(
            name="ordering",
            description='Поле для сортировки: "-rating" (по убыванию рейтинга), "create_date" (по дате создания). По умолчанию: "-create_date".',
            required=False,
            type=str,
            examples=[
                OpenApiExample(
                    "Пример сортировки по дате создания новые с верху",
                    value="-create_date",
                ),
                OpenApiExample(
                    "Пример сортировки по рейтингу, рейтинговые с верху",
                    value="-rating",
                ),
            ],
        ),
        OpenApiParameter(
            name="page",
            description="Номер страницы для пагинации.",
            required=False,
            type=int,
            examples=[OpenApiExample("Пример запроса страницы", value=1)],
        ),
        OpenApiParameter(
            name="page_size",
            description="Кол-во элементов на странице",
            required=False,
            type=int,
            examples=[
                OpenApiExample(
                    "Пример запроса кол-ва элементов на странице. По умолчанию 10",
                    value=10,
                )
            ],
        ),
    ],
    examples=[
        OpenApiExample(
            "Пример успешного ответа",
            value={
                "count": 100,
                "next": "http://example.com/api/recipes/?page=2",
                "previous": None,
                "results": [
                    {
                        "id": 1,
                        "title": "Шоколадный торт",
                        "all_products": ["Шоколад", "Мука", "Сахар"],
                        "image": "http://example.com/media/recipe1.jpg",
                        "likes": 50,
                        "total_views": 200,
                        "cooking_time": 60,
                        "cal_100_gram": 300,
                    },
                    {
                        "id": 2,
                        "title": "Паста Болоньезе",
                        "all_products": ["Паста", "Мясо", "Томатный соус"],
                        "image": "http://example.com/media/recipe2.jpg",
                        "likes": 30,
                        "total_views": 150,
                        "cooking_time": 45,
                        "cal_100_gram": 250,
                    },
                ],
            },
            description="Пример успешного ответа с данными рецептов.",
        )
    ],
)
# @method_decorator(cache_page(60 * 15), name='dispatch') #Декоратор кеширует страницу и результаты фильтров на 15 мин.
class GetAllOpenRecipes(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GetAllOpenRecipesSerializer

    queryset = (
        OpenRecipe.objects.prefetch_related("products")
        .annotate(rating=F("likes") + F("total_views"))
        .defer("instructions", "description", "create_date", "json_products")
        .distinct()
    )

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AllOpenRecipesFilter

    ordering_fields = ["rating", "create_date"]
    ordering = ["-create_date"]  # default - '-create_date'

    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = "page_size"


class GetOpenRecipe(generics.GenericAPIView):
    serializer_class = GetOpenRecipeSerializer
    permission_classes = [permissions.AllowAny]

    """
    Апи принимает айди рецепта, и отдаёт детали рецепта. 
    При вызове рецепта, в редисе сохраняется данные о всех рецептах которые просмотрел пользователь,если он авторизован,
    время жизни данного ключа 1 месяц.
    Так же устанавливается счётчик для просмотров каждому рецепту, где каждый пользователь который в 1 райз вызывает рецепт,
    будет увеличивать счётчик на 1.
    Каждую 1 минуту запускается переодическая задача которая, проходит по всем ключам-счётчикам для рецепта и обновляет 
    поля просмотров, а затем удаляет эти ключи.  
    """

    @extend_schema(
        description="""
                Этот эндпоинт принимает ID рецепта и возвращает детали рецепта. 
                При этом данные о просмотре рецепта сохраняются в Redis:
                - Если пользователь авторизован, сохраняются данные о рецепте, который он просмотрел, с истечением срока действия через месяц.
                - Также увеличивается счетчик просмотров для рецепта. Если это первый просмотр, счетчик создается.
                - Каждую минуту запускается периодическая задача, которая обновляет счетчики просмотров и очищает устаревшие ключи.
            """,
        summary="Получение деталей рецепта",
        examples=[
            OpenApiExample(
                "Пример запроса на получение деталей рецепта",
                value={"open_recipe_pk": 1},
                description="Запрос содержит идентификатор рецепта для получения его данных.",
            ),
            OpenApiExample(
                "Пример успешного ответа",
                value={
                    "detail": {
                        "id": 1,
                        "title": "Курица в молоке.",
                        "recipe_category": "Блюда из курицы",
                        "update_date": "2025-01-13T17:11:39.835027+03:00",
                        "likes": 2,
                        "total_views": 4,
                        "type": "hot",
                        "instructions": [],
                        "image": "/media/img/no_photo.png",
                        "CPCF": {
                            "total_calories": 2471,
                            "total_protein": 27,
                            "total_fat": 14,
                            "total_carbohydrates": 1,
                        },
                        "json_products": {"Курица": 1300, "Молоко": 100},
                        "cooking_time": 0,
                    }
                },
                description="Ответ содержит подробности о рецепте.",
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Пример ошибки, если рецепт не найден",
                value={"detail": "Такого рецепта не существует."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipe = OpenRecipe.objects.get(pk=serializer.validated_data["open_recipe_pk"])
        serializer = OpenRecipeDetailSerializer(recipe)

        if request.user.is_authenticated:
            user = request.user.id
            check_like = Like.objects.filter(user=user, recipe=recipe).exists()
        else:
            check_like = False

        redis_host = os.environ.get("CELERY_BROKER_URL", None)

        if redis_host:
            redis_client = redis.Redis(host="redis", port=6379)
        else:
            redis_client = redis.Redis(host="localhost", port=6379)

        if redis_client.sismember(f"user_{request.user.id}", recipe.pk):
            pass
        else:
            redis_client.sadd(f"user_{request.user.id}", recipe.pk)
            redis_client.expire(f"user_{request.user.id}", 2630000)  # время жизни ключа 1 месяца
            if redis_client.get(f"recipe_{recipe.pk}"):
                redis_client.incr(f"recipe_{recipe.pk}")
            else:
                redis_client.set(f"recipe_{recipe.pk}", 1)
                redis_client.expire(f"recipe_{recipe.pk}", 2630000)  # время жизни ключа 1 месяц

        return Response(
            {"detail": serializer.data, "check_user_like": {"like": bool(check_like)}},
            status=status.HTTP_200_OK,
        )


class SetLike(generics.GenericAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="""
                Этот эндпоинт позволяет пользователю поставить или удалить лайк для рецепта.
                Если лайк для данного рецепта пользователем еще не поставлен, то он будет создан.
                Если лайк уже существует, он будет удален.
            """,
        summary="Создание/удаление лайка рецепта",
        examples=[
            OpenApiExample(
                "Пример запроса на создание лайка",
                value={"open_recipe_pk": 1},
                description="Запрос содержит ID рецепта, к которому пользователь ставит лайк.",
            ),
            OpenApiExample(
                "Пример успешного ответа при создании лайка",
                value={"detail": "Like успешно создан"},
                description="Если лайк еще не поставлен, он будет создан.",
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Пример успешного ответа при удалении лайка",
                value={"detail": "Like удален"},
                description="Если лайк уже существует, он будет удален.",
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Пример ошибки, если пользователь не авторизован",
                value={"detail": "Неверный токен или пользователь не авторизован"},
                description="Если пользователь не авторизован, будет возвращена ошибка.",
                response_only=True,
                status_codes=["401"],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        open_recipe = serializer.validated_data["open_recipe_pk"]

        try:
            like = Like.objects.get(user=user, recipe=open_recipe)
        except Like.DoesNotExist:
            like = Like.objects.create(
                user=user,
                recipe=open_recipe,
            )
            return Response({"detail": "Like успешно создан"}, status=status.HTTP_201_CREATED)

        if like:
            like.delete()
            return Response({"detail": "Like удален"}, status=status.HTTP_200_OK)
