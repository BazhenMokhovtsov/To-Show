import datetime
import math
import os
from functools import reduce
from operator import and_, or_

import redis
from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, F, Q, Sum
from recipes.models.open_recipe import OpenRecipe

from .serializers.open_recipe import *

User = get_user_model()


@shared_task(name="update_open_recipe_total_views_task")
def update_open_recipe_total_views_task():
    redis_host = os.environ.get("CELERY_BROKER_URL", None)
    if redis_host:
        redis_client = redis.Redis(host="redis", port=6379)
    else:
        redis_client = redis.Redis(host="localhost", port=6379)

    recipe_keys = redis_client.keys("recipe_*")
    for key in recipe_keys:
        recipe_id = key.decode().split("_")[1]
        recipe_views = int(redis_client.get(key).decode())

        OpenRecipe.objects.filter(pk=recipe_id).update(total_views=F("total_views") + recipe_views)

        redis_client.delete(key)
