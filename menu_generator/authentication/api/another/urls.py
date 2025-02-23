from django.urls import path

from .views import *

urlpatterns = [
    path(
        "remember-password/first-step/",
        RememberPasswordFirstStep.as_view(),
        name="remember_password_first_step",
    ),
    path(
        "remember-password/second-step/",
        RemeberPasswordSecondStep.as_view(),
        name="remember_password_second_step",
    ),
    path(
        "remember-password/set-password/",
        RememberPasswordSetPassword.as_view(),
        name="remember_password_set_password",
    ),
]
