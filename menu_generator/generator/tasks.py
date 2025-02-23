import datetime
import random
from functools import reduce
from operator import and_, or_

from celery import shared_task
from django.db.models import CharField, Count, Q, Value
from recipes.models.open_recipe import OpenRecipe
from recipes.models.product import Product
from recipes.models.user_recipe import UserRecipe
from rest_framework.response import Response


# TODO: оптимизировать код
# TODO: посмотреть возможность кэширования
# TODO: посмотреть другие методы ускорения сервера
@shared_task(name="generate_menu_task")
def generate_menu_task(
    user_id,
    days,
    one_day,
    meal_times,
    db_choice,
    no_repeat,
    exclude_products,
    exclude_key_words,
    max_number_of_products,
    calories_min,
    calories_max,
    time_cooking,
    include_products,
):

    order_meal_time = {
        "breakfast": ["hot", "salads", "snacks", "baking", "billets", "desserts"],
        "lunch": ["soups", "hot", "salads"],
        "after_tea": ["baking", "desserts"],
        "snack": ["billets", "snacks"],
        "dinner": ["hot", "salads"],
    }
    order_days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    # Создаем переменную, куда будем складировать все нужные фильтры бд
    combined_filters = Q()

    # Проверяем какие указаны время приема пищи
    if meal_times:
        for meal_time in meal_times:
            # Так как мы используем мультиселект, то проверка meal_time__contains
            combined_filters |= Q(meal_time__contains=meal_time)

    # Проверяем какие ключевые слова надо исключить из бд. Делаем с помощью ~Q
    if exclude_key_words:
        for key_word in exclude_key_words:
            combined_filters &= ~Q(title__contains=key_word)

    # Проверяем какие продукты необходимо исключить
    if exclude_products:
        for product in exclude_products:
            # Если название указано как категория, убираем все продукты этой категории
            if product.get("is_category"):
                combined_filters &= ~Q(products__category__title=product["title"])
            else:
                combined_filters &= ~Q(products__title=product["title"])

    # Проверяем, стоит ли ограничение на время приготовления
    if time_cooking:
        combined_filters &= Q(cooking_time__lte=time_cooking)

    # Проверяем, стоит ли ограничение на каллории От
    if calories_min:
        combined_filters &= Q(total_calories__gte=calories_min)

    # Проверяем, стоит ли ограничение на каллориии До
    if calories_max:
        combined_filters &= Q(total_calories__lte=calories_max)

    # Применяем все фильтры к бд
    if "open_recipe" in db_choice:
        db_open_recipes = OpenRecipe.objects.filter(combined_filters).prefetch_related("products")
    else:
        db_open_recipes = None

    if "user_recipe" in db_choice and user_id:
        db_user_recipes = UserRecipe.objects.filter(user__pk=user_id)
        db_user_recipes = db_user_recipes.filter(combined_filters).prefetch_related("products")
    else:
        db_user_recipes = None

    # Так как необходимо использовать аннотацию для добавления нового поля,
    # то фильтрация по количеству продуктов происходит после основной фильтрации.
    if max_number_of_products:
        if db_open_recipes is not None:
            db_open_recipes = db_open_recipes.annotate(
                total_products=Count("products", distinct=True)
            ).filter(total_products__lte=max_number_of_products)
        if db_user_recipes is not None:
            db_user_recipes = db_user_recipes.annotate(
                total_products=Count("products", distinct=True)
            ).filter(total_products__lte=max_number_of_products)

    # Для дальнейшей работы создаем список, куда будем заносить ПК рецептов,
    # которые необходимо исключить
    excluded_recipe_ids = [["user"], ["open"]]

    # Проверяем, есть ли рецепты, которые должны обязательно присутствовать в генерации
    recipes_with_products = []

    # TODO: Использовать продукты не м2м, а product_json
    # TODO: Посмотреть время кода отработки разных частей
    if include_products:
        for product_data in include_products:
            # Чтобы не производить каждый раз фильтрацию, создаем переменную куда
            # будем складировать фильтры
            include_products_filter = Q()
            # Получаем данные которые нам передали
            meal_time = product_data.get("meal_time")
            products = product_data.get("products")
            key_word = product_data.get("key_word")
            all_days = product_data.get("all_days")
            # Так как у каждого приема пищи свои параметры, устанавливаем значения
            # в зависимости от времени према пищи
            if meal_time:
                include_products_filter &= Q(
                    meal_time__contains=meal_time, type__in=order_meal_time[meal_time]
                )

            # Проверяем есть ли параметр ключевое слово
            if key_word:
                include_products_filter &= Q(title__icontains=key_word)

            user_recipe = None
            open_recipe = None

            # Применяем фильтры и получаем случайный рецепт
            if db_user_recipes is not None:
                user_recipes_qs = db_user_recipes.filter(include_products_filter)
                # Исключаем продукты
                user_recipes_qs = user_recipes_qs.filter(
                    reduce(and_, [Q(json_products__has_key=key) for key in products])
                ).only("pk", "title", "meal_time", "type")
                # Выбираем случайную запись.
                ur_list = user_recipes_qs.values_list("pk")
                ur_count = len(ur_list)
                if ur_count > 0:
                    user_recipe = user_recipes_qs[random.randint(0, ur_count - 1)]
                else:
                    user_recipe = None

            if db_open_recipes is not None:
                open_recipes_qs = db_open_recipes.filter(include_products_filter).distinct()
                # Исключаем продукты
                open_recipes_qs = open_recipes_qs.filter(
                    reduce(and_, [Q(json_products__has_key=key) for key in products])
                ).only("pk", "title", "meal_time", "type")
                # Выбираем случайную запись.
                or_list = open_recipes_qs.values_list("pk")
                or_count = len(or_list)
                if or_count > 0:
                    open_recipe = open_recipes_qs[random.randint(0, or_count - 1)]
                else:
                    open_recipe = None

            # Если есть совпадения в обоих бд, то выбираем случайный рецепт
            # и заносим его в список для исключений.
            # В список рецептов по продуктам передаю так же флаг "На все дни"

            if user_recipe and open_recipe:
                selected_recipe = random.choice([user_recipe, open_recipe])
                recipes_with_products.append([selected_recipe, all_days])
                if selected_recipe == user_recipe:
                    excluded_recipe_ids[0].append(selected_recipe.pk)
                else:
                    excluded_recipe_ids[1].append(selected_recipe.pk)

            elif user_recipe:
                recipes_with_products.append([user_recipe, all_days])
                excluded_recipe_ids[0].append(user_recipe.pk)

            elif open_recipe:
                recipes_with_products.append([open_recipe, all_days])
                excluded_recipe_ids[1].append(open_recipe.pk)

    # Если список рецептов по продуктам пустой, то ставим значение None
    if not recipes_with_products:
        recipes_with_products = None

    # Проверяем, если стоит без повторений - удаляем лишнее и очищаем список
    if no_repeat:
        if len(excluded_recipe_ids[0]) > 1:
            db_user_recipes = db_user_recipes.exclude(pk__in=excluded_recipe_ids[0][1:])
            excluded_recipe_ids[0] = ["user"]
        if len(excluded_recipe_ids[1]) > 1:
            db_open_recipes = db_open_recipes.exclude(pk__in=excluded_recipe_ids[1][1:])
            excluded_recipe_ids[1] = ["open"]

    # Переводим данные в словари и объеденяем их
    if db_open_recipes is not None:
        opr = list(
            db_open_recipes.values("pk", "title", "type", "meal_time").annotate(
                db_model=Value("open_recipe", output_field=CharField())
            )
        )
    else:
        opr = None

    if db_user_recipes is not None:
        usr = list(
            db_user_recipes.values("pk", "title", "type", "meal_time").annotate(
                db_model=Value("user_recipe", output_field=CharField())
            )
        )
    else:
        usr = None

    if opr and usr:
        all_recipes = opr + usr
    else:
        all_recipes = opr if opr else usr

    recipe_dict = {f"{recipe['pk']}:{recipe['db_model']}": recipe for recipe in all_recipes}

    # Генерируем!
    result = {}

    # создаем словарь для одного дня
    if one_day:
        for meal_time in order_meal_time:
            if meal_time in meal_times:
                result[meal_time] = None
                if meal_time == "lunch":
                    result[meal_time] = {"soups": None, "hot": None, "salads": None}
                if meal_time == "dinner":
                    result[meal_time] = {"hot": None, "salads": None}

    # создаем словарь для нескольких дней
    else:
        for day in order_days:
            if day in days:
                result[day] = {}
                for meal_time in order_meal_time:
                    if meal_time in meal_times:
                        result[day][meal_time] = None
                        if meal_time == "lunch":
                            result[day][meal_time] = {
                                "soups": None,
                                "hot": None,
                                "salads": None,
                            }
                        if meal_time == "dinner":
                            result[day][meal_time] = {"hot": None, "salads": None}

    def get_random_recipe(meal_time, many_types, type=None):
        access_recipes = []
        if many_types:
            for recipe in recipe_dict.values():
                if meal_time in recipe["meal_time"] and recipe["type"] == type:
                    access_recipes.append(recipe)
        else:
            for recipe in recipe_dict.values():
                if (
                    meal_time in recipe["meal_time"]
                    and recipe["type"] in order_meal_time[meal_time]
                ):
                    access_recipes.append(recipe)

        if access_recipes:
            selected_recipe = random.choice(access_recipes)
            if no_repeat:
                recipe_dict.pop(f"{selected_recipe['pk']}:{selected_recipe['db_model']}")
            return selected_recipe["title"]
        else:
            return None

    if one_day:
        for meal_time in result:
            if meal_time == "breakfast" or meal_time == "after_tea" or meal_time == "snack":
                for recipe, mark_all_days in recipes_with_products:
                    if (
                        recipe.type in order_meal_time[meal_time]
                        and meal_time in recipe.meal_time
                        and result[meal_time] is None
                    ):
                        result[meal_time] = {
                            "recipe": recipe.title,
                            "find_by_products": True,
                        }
                        recipes_with_products.remove([recipe, mark_all_days])
                if result[meal_time] is None:
                    result[meal_time] = get_random_recipe(meal_time, many_types=False)
                if result[meal_time] is None:
                    result[meal_time] = "Нет рецепта"

            if meal_time == "lunch" or meal_time == "dinner":
                for type in result[meal_time]:
                    for recipe, mark_all_days in recipes_with_products:
                        if (
                            recipe.type == type
                            and meal_time in recipe.meal_time
                            and result[meal_time][type] is None
                        ):
                            result[meal_time][type] = {
                                "recipe": recipe.title,
                                "find_by_products": True,
                            }
                            recipes_with_products.remove([recipe, mark_all_days])
                    if result[meal_time][type] is None:
                        result[meal_time][type] = get_random_recipe(
                            meal_time, many_types=True, type=type
                        )
                    if result[meal_time][type] is None:
                        result[meal_time][type] = "Нет рецепта"
    else:
        for day in result:
            for meal_time in result[day]:
                if meal_time == "breakfast" or meal_time == "after_tea" or meal_time == "snack":
                    if recipes_with_products:
                        for recipe, mark_all_days in recipes_with_products:
                            if (
                                recipe.type in order_meal_time[meal_time]
                                and meal_time in recipe.meal_time
                                and result[day][meal_time] is None
                            ):
                                result[day][meal_time] = {
                                    "recipe": recipe.title,
                                    "find_by_products": True,
                                    "all_days": mark_all_days,
                                }
                                recipes_with_products.remove([recipe, mark_all_days])
                                if mark_all_days:
                                    for _day in order_days:
                                        result[_day][meal_time] = {
                                            "recipe": recipe.title,
                                            "find_by_products": True,
                                            "all_days": mark_all_days,
                                        }

                    if result[day][meal_time] is None:
                        result[day][meal_time] = get_random_recipe(meal_time, many_types=False)
                    if result[day][meal_time] is None:
                        result[day][meal_time] = "Нет рецепта"

                if meal_time == "lunch" or meal_time == "dinner":
                    for type in result[day][meal_time]:
                        if recipes_with_products:
                            for recipe, mark_all_days in recipes_with_products:
                                if (
                                    recipe.type == type
                                    and meal_time in recipe.meal_time
                                    and result[day][meal_time][type] is None
                                ):
                                    result[day][meal_time][type] = {
                                        "recipe": recipe.title,
                                        "find_by_products": True,
                                        "all_days": mark_all_days,
                                    }
                                    recipes_with_products.remove([recipe, mark_all_days])
                                    if mark_all_days:
                                        for _day in order_days:
                                            result[_day][meal_time] = {
                                                "recipe": recipe.title,
                                                "find_by_products": True,
                                                "all_days": mark_all_days,
                                            }

                        if result[day][meal_time][type] is None:
                            result[day][meal_time][type] = get_random_recipe(
                                meal_time, many_types=True, type=type
                            )
                        if result[day][meal_time][type] is None:
                            result[day][meal_time][type] = "Нет рецепта"

    return result
