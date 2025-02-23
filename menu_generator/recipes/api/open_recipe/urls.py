from django.urls import path

from .views import *
from recipes.AutocompleteView.views import ProductAutocomplete

urlpatterns = [
    path(
        "open-recipes/get-all-open-recipes/",
        GetAllOpenRecipes.as_view(),
        name="get_all_open_recipes",
    ),
    path("open-recipes/get-open-recipe/", GetOpenRecipe.as_view(), name="get_open_recipe"),
    path("open-recipes/set-like/", SetLike.as_view(), name="set_like"),
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
]
