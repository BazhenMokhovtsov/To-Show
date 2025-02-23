from functools import reduce
from operator import or_

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from mptt.models import TreeForeignKey
from multiselectfield import MultiSelectField
from PIL import Image
from pytils.translit import slugify

from .instruction import Instruction
from .product import Product
from .recipe_category import RecipeCategory

User = get_user_model()


def upload_image(instance, filename):
    slug_title = slugify(instance.title)
    filename_befor_dot = slugify(filename.split(".")[0])
    return (
        f"open_recipe_{slug_title}_id_{instance.id}/{filename_befor_dot}.{filename.split('.')[1]}"
    )


class OpenRecipe(models.Model):
    MEAL_TIME = {
        "breakfast": "Завтрак",
        "lunch": "Обед",
        "after_tea": "Полдник",
        "snack": "Перекус",
        "dinner": "Ужин",
    }

    TYPE_RECIPE = {
        "soups": "Супы",
        "hot": "Горячее",
        "salads": "Салаты",
        "snacks": "Закуски",
        "baking": "Выпечка",
        "Sauces and marinades": "Соусы и маринады",
        "billets": "Заготовки",
        "drinks": "Напитки",
        "desserts": "Дессерты",
        "garnish": "Гарниры",
    }

    title = models.CharField(max_length=200, unique=True, verbose_name="Название рецепта")
    description = models.TextField(
        max_length=3000, null=True, blank=True, verbose_name="Описание рецепта"
    )

    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания рецепта")
    update_date = models.DateTimeField(auto_now=True, verbose_name="Дата обновления рецепта")

    category = TreeForeignKey(
        RecipeCategory,
        on_delete=models.SET_NULL,
        related_name="open_recipes",
        null=True,
        blank=True,
        verbose_name="Категория рецепта",
    )
    products = models.ManyToManyField(
        Product, related_name="recipes", blank=True, verbose_name="Продукты рецепта"
    )
    json_products = models.JSONField(
        default=dict, null=True, blank=True, verbose_name="JSON продукты рецепта"
    )

    image = models.ImageField(
        upload_to=upload_image,
        blank=True,
        null=True,
        verbose_name="Изображение рецепта",
    )
    type = models.CharField(
        max_length=50,
        choices=TYPE_RECIPE.items(),
        blank=False,
        verbose_name="Тип рецепта",
    )
    meal_time = MultiSelectField(
        choices=MEAL_TIME.items(), blank=False, verbose_name="Время приёма"
    )
    instructions = models.ManyToManyField(
        Instruction, related_name="open_recipes", verbose_name="Инструкции к рецепту"
    )
    cooking_time = models.PositiveIntegerField(
        null=True, blank=True, default=0, verbose_name="Время приготовления"
    )

    likes = models.IntegerField(db_index=True, default=0, verbose_name="Лайки")
    total_views = models.IntegerField(
        default=0, db_index=True, verbose_name="Количество просмотров"
    )

    cal_100_gram = models.FloatField(default=0, verbose_name="Калорийность на 100 грамм")
    total_calories = models.FloatField(default=0, verbose_name="Калорийность рецепта")
    total_protein = models.FloatField(default=0, verbose_name="Кол-во белков в рецепте")
    total_fat = models.FloatField(default=0, verbose_name="Жирность рецепта")
    total_carbohydrates = models.FloatField(default=0, verbose_name="Кол-во углеводов в рецепте")

    objects = models.Manager()

    # юзер. тайтл. милтайм индексация.
    class Meta:
        ordering = ["-update_date"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["update_date"]),
            models.Index(fields=["category"]),
            models.Index(fields=["type"]),
            models.Index(fields=["meal_time"]),
        ]
        verbose_name = "Открытый рецепт"
        verbose_name_plural = "Открытые рецепты"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        print(f'j_products {self.json_products}')
        self.json_products = {
            key.capitalize(): int(value) for key, value in self.json_products.items()
        }

        super().save(*args, **kwargs)

        if self.json_products:
            keys = self.json_products.keys()
            products = Product.objects.filter(
                reduce(or_, [Q(title__icontains=key) for key in keys])
            )
            self.products.set(products)
        else:
            self.products.clear()

        if self.image:
            img = Image.open(self.image.path)
            if img.width > 300 or img.height > 300:
                new_size = (300, 300)
                img.thumbnail(new_size)
                img.convert("RGB")
                if self.image.path.split(".")[1] != "png":
                    new_path = f"{self.image.path.split('.')[0]}.png"
                    img.save(new_path, format="PNG")
                    self.image.delete()
                    self.image = f"{new_path.split('media/')[1]}"
                    self.save()
                else:
                    img.save(self.image.path, format="PNG")

    def sum_cal_100_gram(self):
        self.cal_100_gram = sum([product.calories for product in self.products.all()])

    def update_CPFC(self):
        self.total_calories = 0
        self.total_protein = 0
        self.total_fat = 0
        self.total_carbohydrates = 0

        for product in self.products.all():
            try:
                product_quantity = self.json_products[str(product.title)]
            except KeyError:
                product_quantity = 0
            if product.brutto == "pieces":
                self.total_calories += product.calories * product_quantity
                self.total_protein += product.protein * product_quantity
                self.total_fat += product.fat * product_quantity
                self.total_carbohydrates += product.carbohydrates * product_quantity

            if product.brutto == "grams":
                self.total_calories += product.calories * product_quantity / 100
                self.total_protein += product.protein * product_quantity / 100
                self.total_fat += product.fat * product_quantity / 100
                self.total_carbohydrates += product.carbohydrates * product_quantity / 100


@receiver(post_save, sender=OpenRecipe)
def update_json_products(sender, instance, **kwargs):
    instance.update_CPFC()

    OpenRecipe.objects.filter(pk=instance.pk).update(
        total_calories=instance.total_calories,
        total_protein=instance.total_protein,
        total_fat=instance.total_fat,
        total_carbohydrates=instance.total_carbohydrates,
    )


@receiver(m2m_changed, sender=OpenRecipe.products.through)
def update_CPFC(sender, instance, action, *args, **kwargs):
    if action in ["post_add", "post_remove"]:
        instance.update_CPFC()
        instance.save()


@receiver(m2m_changed, sender=OpenRecipe.products.through)
def sum_cal_100_gram(sender, instance, action, *args, **kwargs):
    if action in ["post_add", "post_remove"]:
        instance.sum_cal_100_gram()
        instance.save()


