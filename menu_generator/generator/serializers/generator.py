from functools import reduce
from operator import or_

from django.db.models import Q
from recipes.models.open_recipe import OpenRecipe
from recipes.models.product import Product
from recipes.models.user_recipe import UserRecipe
from rest_framework import serializers


class GeneratorMenuSerializer(serializers.Serializer):
    DAYS = {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
        "saturday": "Суббота",
        "sunday": "Воскресенье",
    }

    DB_CHOICE = {
        "open_recipe": "Открытые рецепты",
        "user_recipe": "Пользовательские рецепты",
    }

    days = serializers.MultipleChoiceField(
        choices=DAYS,
        required=False,
        write_only=True,
        default=[
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
    )
    one_day = serializers.BooleanField(required=False, write_only=True, default=False)
    meal_time = serializers.MultipleChoiceField(
        choices=UserRecipe.MEAL_TIME,
        required=False,
        write_only=True,
        default=["breakfast", "lunch", "after_tea", "snack", "dinner"],
    )
    db_choice = serializers.MultipleChoiceField(
        choices=DB_CHOICE,
        required=False,
        write_only=True,
        default=["open_recipe", "user_recipe"],
    )
    no_repeat = serializers.BooleanField(required=False, write_only=True, default=False)

    exclude_products = serializers.ListField(required=False, write_only=True, default=[])
    exclude_key_words = serializers.ListField(required=False, write_only=True, default=[])
    include_products = serializers.ListField(
        required=False, write_only=True, allow_null=True, default=[]
    )

    calories_min = serializers.IntegerField(
        required=False, write_only=True, default="null", allow_null=True
    )
    calories_max = serializers.IntegerField(
        required=False, write_only=True, default="null", allow_null=True
    )
    time_cooking = serializers.IntegerField(
        required=False, write_only=True, default="null", allow_null=True
    )
    max_number_of_products = serializers.IntegerField(
        required=False, write_only=True, default="null", allow_null=True
    )

    def validate(self, attrs):
        exclude_key_words = attrs.get("exclude_key_words")
        if exclude_key_words:
            for key_word in exclude_key_words:
                if len(key_word) < 2:
                    raise serializers.ValidationError(
                        "Ключевые слова не могут быть короче 2 символов."
                    )

        max_number_of_products = attrs.get("max_number_of_products")
        if max_number_of_products:
            if max_number_of_products < 0:
                raise serializers.ValidationError(
                    "Количество продуктов не может быть отрицательным."
                )

        time_cooking = attrs.get("time_cooking")
        if time_cooking:
            if time_cooking < 0:
                raise serializers.ValidationError(
                    "Время приготовления не может быть отрицательным."
                )

        calories_min = attrs.get("calories_min")
        calories_max = attrs.get("calories_max")

        if calories_min:
            if calories_min < 0:
                raise serializers.ValidationError("Калории не может быть отрицательным.")
            if calories_max:
                if calories_max <= calories_min:
                    raise serializers.ValidationError(
                        "Калории ДО не должны быть больше или равны калориям ОТ."
                    )

        return attrs


class TaksIdSerializer(serializers.Serializer):
    task_id = serializers.CharField(required=True)


# {
#   "days": [
#     "saturday",
#     "sunday",
#     "thursday",
#     "wednesday",
#     "tuesday",
#     "friday",
#     "monday"
#   ],
#   "one_day": false,
#   "meal_time": [
#     "snack",
#     "dinner",
#     "after_tea",
#     "breakfast",
#     "lunch"
#   ],
#   "db_choice": [
#     "open_recipe",
#     "user_recipe"
#   ],
#   "no_repeat": true,
#   "exclude_products": [
#       {
#           "title": "Овощная",
#           "is_category": true
#       }
#   ],
#   "exclude_key_words": [],
#   "include_products": [
#       {
#           "meal_time": "breakfast",
#           "products": ["Сливки"],
#           "key_word": "кофе",
#           "all_days": true
#       },
#       {
#           "meal_time": "lunch",
#           "products": ["Лук", "Морковь"],
#           "key_word": "суп",
#           "all_days": false
#       }
#       ],
#   "calories_min": null,
#   "calories_max": null,
#   "time_cooking": null,
#   "max_number_of_products": null
# }
#
