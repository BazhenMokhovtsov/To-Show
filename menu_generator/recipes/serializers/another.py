from django.db.models import DO_NOTHING
from recipes.models.instruction import Instruction
from recipes.models.open_recipe import OpenRecipe
from recipes.models.product import Product
from recipes.models.recipe_category import RecipeCategory
from rest_framework import serializers


class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = ["id", "title", "parent"]
        extra_kwargs = {
            "id": {"read_only": True},
            "title": {"read_only": True},
            "parent": {"read_only": True},
        }


class InstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruction
        fields = ["id", "step", "text", "image"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["title"]

    def to_representation(self, instance):
        return instance.title
