from django.urls import path

from .views import *

urlpatterns = [
    path("generate/", GenerateMenu.as_view(), name="generate"),
    path("generate/check/", CheckResult.as_view(), name="check"),
]
