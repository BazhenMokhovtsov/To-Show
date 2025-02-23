from django.urls import path

from .views import *

urlpatterns = [
    path(
        "open-recipes/search-field-helper/",
        SearchHelpers.as_view(),
        name="search-field-helper",
    ),
]
