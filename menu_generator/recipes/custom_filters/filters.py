import datetime

from django.db.models import Count, Q
from django_filters import rest_framework as filters
from recipes.models.open_recipe import OpenRecipe

"""
Этот класс предоставляет различные фильтры для поиска и фильтрации рецептов по  
различным критериям, таким как поисковый запрос, включённые/исключённые продукты,  
время приёма пищи, тип блюда, время приготовления и калорийность.
"""


class AllOpenRecipesFilter(filters.FilterSet):
    start = datetime.datetime.now()

    def filter_queryset(self, queryset):
        # start = datetime.datetime.now()
        self.filtered_queryset = queryset

        # Применяем все фильтры, кроме поиска
        for name, value in self.form.cleaned_data.items():
            if name != "search_query" and value not in [
                None,
                "",
                [],
            ]:  # если форма поиска не заполненна, фильтруем по заполенныи фильтрам и устанавливаем значение фильтруемого кверисета
                # print(name, value)
                self.filtered_queryset = self.filters[name].filter(self.filtered_queryset, value)

        # Применяем поиск в конце
        search_query = self.form.cleaned_data.get("search_query")
        if search_query:
            # print('search_query', search_query)
            self.filtered_queryset = self.search_filter(
                self.filtered_queryset, "search_query", search_query
            )

        # print(datetime.datetime.now() - start, "время работы фильтров.")
        return self.filtered_queryset

    # Поиск рецептов по ключевым словам.
    search_query = filters.CharFilter(
        method="search_filter",
        label="Поиск рецептов по Заголовку, Ингредиенту и Категории ингредиента",
    )

    def search_filter(self, queryset, name, value):
        # print(queryset.count(), "queryset quantity before searching")
        if not value:
            return queryset
        else:
            terms = value.split(" ")
            for term in terms:
                queryset = queryset.filter(
                    Q(title__icontains=term)
                    | Q(products__title__icontains=term)
                    | Q(products__category__title__icontains=term)
                )
        # print(queryset.count(), "queryset quantity after searching")
        return queryset

    # Фильтрация рецептов по исключенным продуктам
    exclude_products = filters.CharFilter(
        method="exclude_products_filter", label="Исключённые продукты"
    )

    def exclude_products_filter(self, queryset, name, value):
        if not value:
            return queryset
        else:
            excluded_products = value.split(" ")
            query = Q()

            for product in excluded_products:
                query |= Q(products__title__icontains=product) | Q(
                    products__category__title__icontains=product
                )

            return queryset.exclude(query)

    # Фильтрация рецептов по включённым продуктам.
    include_products = filters.CharFilter(
        method="include_products_filter", label="Входящие продукты"
    )

    def include_products_filter(self, queryset, name, value):
        if not value:
            return queryset
        else:
            # print(queryset.count(), "queryset quantity before filtering")
            include_products = value.split(" ")
            for term in include_products:
                queryset = queryset.filter(
                    Q(products__title__icontains=term)
                    | Q(products__category__title__icontains=term)
                )

        # print(queryset.count(), "queryset quantity after filtering")
        return queryset

    # Фильтрация рецептов по Типу приёма пищи.
    meal_time = filters.MultipleChoiceFilter(
        choices=list(OpenRecipe.MEAL_TIME.items()),
        field_name="meal_time",
        lookup_expr="contains",
        label="Тип приёма пищи",
    )

    # Фильтрация рецептов по Типу блюда
    type = filters.ChoiceFilter(
        choices=list(OpenRecipe.TYPE_RECIPE.items()),
        field_name="type",
        lookup_expr="contains",
        label="Тип блюда",
    )

    # Фильтрация рецептов по максимальному кол-ву продуктов в рецепте.
    max_products_quantity = filters.NumberFilter(
        method="max_products_count_filter", label="Максимальное количество продуктов"
    )

    def max_products_count_filter(self, queryset, name, value):
        if not value:
            return queryset
        else:
            queryset = queryset.annotate(product_count=Count("products")).filter(
                product_count__lte=value
            )
            return queryset

    # Фильтрация рецептов по максимальному времени приготовления.
    cooking_time = filters.NumberFilter(
        field_name="cooking_time", lookup_expr="lte", label="Максимальное время готовки"
    )
    # Фильтрация рецептов по максимальной каллорийности блюда на 100г.
    max_cal_100_gram = filters.NumberFilter(
        field_name="cal_100_gram",
        lookup_expr="lte",
        label="Максимальное количество калорий на 100г.",
    )
