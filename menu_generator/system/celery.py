# celery -A system worker -B -l info --concurrency=5
# celery -A system worker -l info --concurrency=20 -n=worker_gen_1 --hostname=worker2@%h --queues=generate_menu_queue --prefetch-multiplier=4 --soft-time-limit=200 --time-limit=300
# celery -A system worker -l info --concurrency=20 -n=worker_filter_1 --hostname=worker2@%h --queues=show_filtered_open_recipes_queue --prefetch-multiplier=4 --soft-time-limit=200 --time-limit=300
# celery -A system worker -l info --concurrency=20 -n=worker_all_recipes_1 --hostname=worker2@%h --queues=get_all_open_recipes_queue --prefetch-multiplier=4 --soft-time-limit=200 --time-limit=300
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "system.settings")
app = Celery("menu_generator")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.broker_connection_retry_on_startup = True
app.conf.worker_max_tasks_per_child = 1000  # Перезапуск воркера после 1000 задач
app.conf.worker_max_memory_per_child = 200000  # Перезапуск при использовании более 200MB памяти
app.conf.broker_pool_limit = 10  # Ограничение пула соединений
app.conf.broker_connection_max_retries = 0  # Отключить бесконечные попытки


app.conf.beat_schedule = {
    "check_redis": {
        "task": "update_open_recipe_total_views_task",
        "schedule": crontab(minute="*/5"),
    }
}
