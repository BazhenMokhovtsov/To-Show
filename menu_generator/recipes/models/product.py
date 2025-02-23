from django.contrib.auth import get_user_model
from django.db import models
from mptt.fields import TreeForeignKey

from .product_category import ProductCategory

User = get_user_model()


class Product(models.Model):
    BRUTTO_TYPE = {
        "pieces": "штук",
        "grams": "граммы",
    }

    title = models.CharField(max_length=200, unique=True, verbose_name="Название")
    category = TreeForeignKey(
        ProductCategory, on_delete=models.CASCADE, verbose_name="Категория продукта"
    )
    brutto = models.CharField(
        max_length=50, choices=BRUTTO_TYPE.items(), verbose_name="Единица измерения"
    )

    calories = models.FloatField(verbose_name="Калории", default=0)
    protein = models.FloatField(verbose_name="Белки", default=0)
    fat = models.FloatField(verbose_name="Жиры", default=0)
    carbohydrates = models.FloatField(verbose_name="Углеводы", default=0)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["category"]),
            models.Index(fields=["title", "category"]),
        ]
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.pk}, {self.title}"

    def save(self, *args, **kwargs):
        self.title = self.title.capitalize()
        super().save(*args, **kwargs)
