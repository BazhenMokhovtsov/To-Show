from django.urls import path

from .views import *

urlpatterns = [
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("refresh/", Refresh.as_view(), name="refresh"),
]
