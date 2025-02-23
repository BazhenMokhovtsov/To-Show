from django.contrib.auth import get_user_model
from django.db import models
from PIL import Image
from pytils.translit import slugify

User = get_user_model()


def upload_image(instance, filename):
    username_slug = slugify(instance.user.username)
    filename_befor_dot = slugify(filename.split(".")[0])
    return f"instructions/{username_slug}/{filename_befor_dot}.{filename.split('.')[1]}"


def get_admin():
    try:
        admin = User.objects.get(username="admin")
        return admin
    except User.DoesNotExist:
        return None


class Instruction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=get_admin)
    text = models.TextField(blank=True, verbose_name="Текст")
    step = models.PositiveIntegerField(verbose_name="Шаг")
    image = models.ImageField(
        upload_to=upload_image, blank=True, null=True, verbose_name="Изображение к шагу"
    )
    recipe_id = models.IntegerField(blank=True, null=True, verbose_name="Айди рецепта")
    recipe_title = models.TextField(blank=True, null=True, verbose_name="Название рецепта")

    objects = models.Manager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
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

    def __str__(self):
        return f"Шаг {self.step} к рецепту {self.text}"

    class Meta:
        ordering = ["step"]
        indexes = [
            models.Index(fields=["step"]),
        ]
        verbose_name = "Инструкция"
        verbose_name_plural = "Инструкции"
