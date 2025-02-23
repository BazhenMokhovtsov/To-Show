from django.contrib.auth import get_user_model
from django.db.models import Sum
from recipes.models.like import Like
from recipes.models.open_recipe import OpenRecipe
from recipes.serializers.another import (
    InstructionSerializer,
    ProductSerializer,
    RecipeCategorySerializer,
)
from rest_framework import serializers

User = get_user_model()


class GetAllOpenRecipesSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = OpenRecipe
        fields = [
            "id",
            "title",
            "products",
            "image",
            "likes",
            "total_views",
            "cooking_time",
            "cal_100_gram",
        ]


class GetOpenRecipeSerializer(serializers.ModelSerializer):
    open_recipe_pk = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = OpenRecipe
        fields = ["open_recipe_pk"]

    def validate(self, attrs):
        try:
            OpenRecipe.objects.get(pk=attrs["open_recipe_pk"])
        except OpenRecipe.DoesNotExist:
            raise serializers.ValidationError("Такого рецепта не существует.")
        return attrs


class OpenRecipeDetailSerializer(serializers.ModelSerializer):
    instructions = InstructionSerializer(read_only=True, many=True)
    CPCF = serializers.SerializerMethodField(read_only=True)
    category = RecipeCategorySerializer(read_only=True)

    class Meta:
        model = OpenRecipe
        fields = [
            "id",
            "title",
            "category",
            "update_date",
            "likes",
            "total_views",
            "type",
            "instructions",
            "image",
            "CPCF",
            "json_products",
            "cooking_time",
        ]

    def get_CPCF(self, obj):
        return {
            "total_calories": obj.total_calories,
            "total_protein": obj.total_protein,
            "total_fat": obj.total_fat,
            "total_carbohydrates": obj.total_carbohydrates,
        }


class LikeSerializer(serializers.ModelSerializer):
    open_recipe_pk = serializers.PrimaryKeyRelatedField(
        queryset=OpenRecipe.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = Like
        fields = [
            "open_recipe_pk",
        ]
