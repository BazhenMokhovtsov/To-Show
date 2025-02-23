from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .open_recipe import OpenRecipe

User = get_user_model()


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, default=User, verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(OpenRecipe, on_delete=models.CASCADE, verbose_name="Рецепт")

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        ordering = ["-recipe"]
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_user_recipe_likes")
        ]

        indexes = [models.Index(fields=["user", "recipe"])]

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"


@receiver(post_save, sender=Like)
def update_recipe_likes_count_on_save(sender, instance, *args, **kwargs):
    OpenRecipe.objects.filter(pk=instance.recipe.pk).update(likes=F("likes") + 1)


@receiver(post_delete, sender=Like)
def update_recipe_likes_count_on_delete(sender, instance, *args, **kwargs):
    OpenRecipe.objects.filter(pk=instance.recipe.pk).update(likes=F("likes") - 1)
