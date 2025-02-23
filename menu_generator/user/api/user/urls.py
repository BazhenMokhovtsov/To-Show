from django.urls import path

from .views import *

urlpatterns = [
    path("get-user/", GetUser.as_view(), name="get_user"),
]
