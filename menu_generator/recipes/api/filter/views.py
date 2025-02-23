from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from recipes.models.open_recipe import OpenRecipe
from recipes.models.product import Product
from recipes.models.product_category import ProductCategory
from recipes.serializers.filter import SearchHelpersFieldSerializer
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response

User = get_user_model()


class SearchHelpers(generics.GenericAPIView):
    serializer_class = SearchHelpersFieldSerializer
    permission_classes = [permissions.AllowAny]

    """
    Данные Апи относятся к ПОДСКАЗКАМ а не к результату который будет выдан.
    1. hard Заголовок рецепта, Категория продукта, Название продукта.
    2. medium Название продукта, Категория продукта.
    3. Название продукта.
    
    """

    @extend_schema(
        description="""
                Эндпоинт для поиска подсказок на основе пользовательского ввода.
                Поиск производится по трём уровням сложности:
                - **hard**: поиск по названию рецепта, названию продукта и названию категории продукта.
                - **medium**: поиск по названию продукта и названию категории продукта.
                - **easy**: поиск только по названию продукта.
            """,
        summary="Поиск подсказок по рецептам и продуктам",
        request=SearchHelpersFieldSerializer,
        responses={
            200: SearchHelpersFieldSerializer,
            400: inline_serializer(name="ErrorResponse", fields={"error": serializers.CharField()}),
        },
        examples=[
            OpenApiExample(
                "Пример запроса для режима hard",
                value={"user_input": "кар", "search_method": "hard"},
                request_only=True,
            ),
            OpenApiExample(
                "Пример запроса для режима medium",
                value={"user_input": "кар", "search_method": "medium"},
                request_only=True,
            ),
            OpenApiExample(
                "Пример запроса для режима easy",
                value={"user_input": "кар", "search_method": "easy"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_input = serializer.validated_data["user_input"]
        search_method = serializer.validated_data["search_method"]

        # Хардовая (hard) версия ищет по Заголовку рецепта, Заголовку категории продукта и по Заголовку продукта.
        if search_method == "hard":
            searched_recipe_title_list = OpenRecipe.objects.filter(
                Q(title__icontains=user_input) | Q(title__search=user_input)
            )
            searched_products_list = Product.objects.filter(
                Q(title__icontains=user_input) | Q(title__search=user_input)
            )
            searched_products_category_list = ProductCategory.objects.filter(
                Q(title__icontains=user_input) | Q(title__search=user_input)
            )

            result = {
                "found_by_recipe_title": list(
                    searched_recipe_title_list.values_list("title", flat=True)
                ),
                "found_by_product": list(searched_products_list.values_list("title", flat=True)),
                "found_by_product_category": list(
                    searched_products_category_list.values_list("title", flat=True)
                ),
            }

            serializer = SearchHelpersFieldSerializer(result)

            return Response(serializer.data, status=status.HTTP_200_OK)

        # Медиум(medium) версия ищет по Заголовку продукта и Заголовку Категории продукта.
        if search_method == "medium":
            searched_products_list = Product.objects.filter(
                Q(title__icontains=user_input) | Q(title__search=user_input)
            )
            searched_products_category_list = ProductCategory.objects.filter(
                Q(title__icontains=user_input) | Q(title__search=user_input)
            )

            result = {
                "found_by_product": list(searched_products_list.values_list("title", flat=True)),
                "found_by_product_category": list(
                    searched_products_category_list.values_list("title", flat=True)
                ),
            }

            serializer = SearchHelpersFieldSerializer(result)

            return Response(serializer.data, status=status.HTTP_200_OK)

        # Изи(easy) версия ищет по Заголовку продукта
        if search_method == "easy":
            searched_products_list = Product.objects.filter(
                Q(title__search=user_input) | Q(title__icontains=user_input)
            )

            result = {
                "found_by_product": list(searched_products_list.values_list("title", flat=True)),
            }

            serializer = SearchHelpersFieldSerializer(result)

            return Response(serializer.data, status=status.HTTP_200_OK)
