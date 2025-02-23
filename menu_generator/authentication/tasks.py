from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


@shared_task(name="send_mail_task")
def send_mail_task(subject, message, to_email):
    send_mail(
        subject=subject,
        message=message,
        recipient_list=[to_email],
        from_email=settings.EMAIL_HOST_USER,
        fail_silently=False,
    )
