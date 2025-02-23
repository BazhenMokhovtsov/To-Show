import datetime
import json
import random
from functools import reduce
from operator import and_, or_

from celery import current_app
from celery.result import AsyncResult
from django.contrib.auth import get_user_model
from django.db import connection, reset_queries
from django.db.models import CharField, Count, Max, Q, Value
from django.db.models.functions import Random
from generator.serializers.generator import *
from recipes.models.open_recipe import OpenRecipe
from recipes.models.product import Product
from recipes.models.user_recipe import UserRecipe
from redis import Redis
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .another import *

User = get_user_model()

redis_client = Redis()

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


class GenerateMenu(generics.GenericAPIView):
    serializer_class = GeneratorMenuSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        connection.queries_log.clear()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        # Атрибуты сериализера
        days = data.get("days")
        one_day = data.get("one_day")
        meal_times = data.get("meal_time")
        db_choice = data.get("db_choice")
        no_repeat = data.get("no_repeat")

        exclude_products = data.get("exclude_products")
        exclude_key_words = data.get("exclude_key_words")

        max_number_of_products = data.get("max_number_of_products")
        calories_min = data.get("calories_min")
        calories_max = data.get("calories_max")
        time_cooking = data.get("time_cooking")

        include_products = data.get("include_products")

        if request.user.is_anonymous:
            user_id = None
        else:
            user_id = request.user.id

        task_id = current_app.send_task(
            "generate_menu_task",
            kwargs={
                "user_id": user_id,
                "days": list(days),
                "one_day": one_day,
                "meal_times": list(meal_times),
                "db_choice": list(db_choice),
                "no_repeat": no_repeat,
                "exclude_products": exclude_products,
                "exclude_key_words": exclude_key_words,
                "max_number_of_products": max_number_of_products,
                "calories_min": calories_min,
                "calories_max": calories_max,
                "time_cooking": time_cooking,
                "include_products": include_products,
            },
            queue="generate_menu_queue",
        )

        return Response({"result": str(task_id)}, status=status.HTTP_200_OK)


class CheckResult(generics.GenericAPIView):
    serializer_class = TaksIdSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_id = serializer.validated_data["task_id"]

        task = AsyncResult(task_id)
        try:
            task_result = task.get()
            return Response({"detail": task_result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
