from django.urls import path

from .views import *

urlpatterns = [
    path(
        "user-recipes/list-user-recipes/",
        ListAuthUserRecipes.as_view(),
        name="list_auth_user_recipes",
    ),
    path("user-recipes/get-user-recipe/", GetUserRecipe.as_view(), name="get_user_recipe"),
    path(
        "user-recipes/create-user-recipe/",
        CreateUserRecipe.as_view(),
        name="create_user_recipe",
    ),
    path(
        "user-recipes/create-user-recipe/add-instruction/",
        AddInstructionForUserRecipe.as_view(),
        name="add_instruction_for_user_recipe",
    ),
    path(
        "user-recipes/edit-user-recipe/",
        EditUserRecipe.as_view(),
        name="edit_user_recipe",
    ),
    path(
        "user-recipes/delete-user-recipe/",
        DeleteUserRecipe.as_view(),
        name="delete_user_recipe",
    ),
    path(
        "user-recipes/add-open-recipe-to-user-recipe/",
        AddOpenRecipeToUserRecipe.as_view(),
        name="add_open_recipe_to_user_recipe",
    ),
]
