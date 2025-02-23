from django.contrib.auth import get_user_model
from recipes.models.user_recipe import UserRecipe
from recipes.serializers.another import *
from recipes.serializers.user_recipe import *
from rest_framework import generics, permissions, status
from rest_framework.response import Response

User = get_user_model()


class ListAuthUserRecipes(generics.GenericAPIView):
    serializer_class = ListAuthUserRecipesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        list_recipes = UserRecipe.objects.filter(user=user)
        serializer = ListAuthUserRecipesSerializer(list_recipes, many=True)
        return Response({"detail": serializer.data}, status=status.HTTP_200_OK)


class GetUserRecipe(generics.GenericAPIView):
    serializer_class = GetUserRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user_recipe = UserRecipe.objects.get(pk=serializer.validated_data["user_recipe_pk"])

        recipe_detail = UserRecipeDetailSerializer(user_recipe)
        return Response({"detail": recipe_detail.data}, status=status.HTTP_200_OK)


class CreateUserRecipe(generics.GenericAPIView):
    serializer_class = CreateUserRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_user_recipe = serializer.create(serializer.validated_data)
        new_user_recipe = UserRecipeDetailSerializer(new_user_recipe)

        return Response({"detail": new_user_recipe.data}, status=status.HTTP_201_CREATED)


class AddInstructionForUserRecipe(generics.GenericAPIView):
    serializer_class = AddInstructionForUserRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_recipe_instruction = serializer.create(serializer.validated_data)
        user_recipe_instruction = InstructionSerializer(user_recipe_instruction)
        return Response({"detail": user_recipe_instruction.data}, status=status.HTTP_201_CREATED)


class EditUserRecipe(generics.GenericAPIView):
    serializer_class = EditUserRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_recipe = UserRecipe.objects.get(pk=serializer.validated_data["user_recipe_pk"])
        edit_recipe = serializer.update(user_recipe, serializer.validated_data)
        edit_recipe = UserRecipeDetailSerializer(edit_recipe)

        return Response({"detail": edit_recipe.data}, status=status.HTTP_202_ACCEPTED)


class DeleteUserRecipe(generics.GenericAPIView):
    serializer_class = DeleteUserRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_recipe = UserRecipe.objects.get(pk=serializer.validated_data["user_recipe_pk"])
        user_recipe.instructions.all().delete()
        user_recipe.delete()

        return Response({"detail": "Рецепт успешно удален"}, status=status.HTTP_204_NO_CONTENT)


class AddOpenRecipeToUserRecipe(generics.GenericAPIView):
    serializer_class = AddOpenRecipeToUserRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        open_recipe = OpenRecipe.objects.get(pk=serializer.validated_data["open_recipe_pk"])

        user_recipe = UserRecipe.objects.create(
            user=request.user,
            title=open_recipe.title,
            description=open_recipe.description,
            category=open_recipe.category,
            image=open_recipe.image,
            type=open_recipe.type,
            meal_time=[open_recipe.meal_time],
            edited=True,
            original_recipe=open_recipe,
            json_products=open_recipe.json_products,
        )

        if open_recipe.products.exists():
            user_recipe.products.set(open_recipe.products.all())

        if open_recipe.instructions.exists():
            user_recipe.instructions.set(open_recipe.instructions.all())

        user_recipe = UserRecipeDetailSerializer(user_recipe)

        return Response({"detail": user_recipe.data}, status=status.HTTP_201_CREATED)
