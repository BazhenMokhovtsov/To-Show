from django.urls import path

from .views import *

urlpatterns = [
    path(
        "registration/first-step/",
        RegistrationFirstStep.as_view(),
        name="registration_first_step",
    ),
    path(
        "registration/second-step/",
        RegistrationSecondStep.as_view(),
        name="registration_second_step",
    ),
]
