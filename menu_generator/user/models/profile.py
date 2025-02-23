from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .user import User


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, editable=False, related_name="profile"
    )
    settings = models.JSONField(default=dict, verbose_name="Настройки")

    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    date_update = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    objects = models.Manager()

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"profile: {self.user.username}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
