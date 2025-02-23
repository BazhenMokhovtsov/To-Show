from io import BytesIO

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Пользователь должен иметь username")
        if not email:
            raise ValueError("Пользователь должен иметь email")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username=username, email=email, password=password, **extra_fields)


def upload_image(instanse, filename):
    return f"users/{instanse.username}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=50, unique=True, db_index=True, verbose_name="Имя пользователя"
    )
    email = models.EmailField(max_length=255, unique=True, db_index=True, verbose_name="Почта")
    image = models.ImageField(
        upload_to=upload_image, null=True, blank=True, verbose_name="Изображение"
    )
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    date_update = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_update"]
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["date_update"]),
        ]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.width > 300 or img.height > 300:
                new_size = (300, 300)
                img.thumbnail(new_size)
                img.convert("RGB")
                new_path = f"{self.image.path.split('.')[0]}.png"
                img.save(new_path, format="PNG")
                self.image.delete()
                self.image = f"{new_path.split('media/')[1]}"
                self.save()
