from django.contrib.auth import get_user_model
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()


class ProductCategory(MPTTModel):
    title = models.CharField(max_length=200, unique=True, verbose_name="Название Категории")
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", null=True, blank=True
    )

    class Meta:
        ordering = ["title"]
        indexes = [models.Index(fields=["title"])]
        verbose_name = "Категория продукта"
        verbose_name_plural = "Категории продуктов"

    class MTTPMeta:
        order_insertion_by = ["title"]

    def __str__(self):
        return self.title
