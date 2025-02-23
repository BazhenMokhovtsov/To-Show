from recipes.models.open_recipe import OpenRecipe
from recipes.models.user_recipe import UserRecipe
from rest_framework import serializers

from .another import *


class ListAuthUserRecipesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRecipe
        fields = ["id", "title"]
        extra_kwargs = {
            "title": {"read_only": True},
        }


class GetUserRecipeSerializer(serializers.ModelSerializer):
    user_recipe_pk = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = UserRecipe
        fields = [
            "user_recipe_pk",
        ]


class UserRecipeDetailSerializer(serializers.ModelSerializer):
    instructions = InstructionSerializer(many=True)
    CPFC = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserRecipe
        fields = [
            "id",
            "title",
            "description",
            "category",
            "image",
            "type",
            "meal_time",
            "update_date",
            "CPFC",
            "instructions",
            "edited",
            "original_recipe",
            "cooking_time",
            "json_products",
        ]

    def get_CPFC(self, obj):
        return {
            "calories": obj.total_calories,
            "protein": obj.total_protein,
            "fat": obj.total_fat,
            "carbohydrates": obj.total_carbohydrates,
        }


class CreateUserRecipeSerializer(serializers.ModelSerializer):
    original_recipe = serializers.IntegerField(default="null", required=False, allow_null=True)
    json_products = serializers.JSONField(default={})
    image = serializers.ImageField(required=False, allow_null=True)
    edited = serializers.BooleanField(default=False)
    meal_time = serializers.MultipleChoiceField(choices=UserRecipe.MEAL_TIME, required=False)
    cooking_time = serializers.IntegerField(default=0, required=False)

    class Meta:
        model = UserRecipe
        fields = [
            "title",
            "description",
            "category",
            "image",
            "type",
            "meal_time",
            "update_date",
            "edited",
            "original_recipe",
            "json_products",
            "cooking_time",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        image = validated_data.get("image")
        if image is None:
            image = "img/no_photo.png"
        user_recipe = UserRecipe.objects.create(
            user=user,
            title=validated_data["title"],
            description=validated_data.get("description"),
            category=validated_data["category"],
            image=image,
            type=validated_data["type"],
            meal_time=validated_data["meal_time"],
            json_products=validated_data["json_products"],
            cooking_time=validated_data.get("cooking_time"),
        )

        return user_recipe


class AddInstructionForUserRecipeSerializer(serializers.ModelSerializer):
    user_recipe_pk = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Instruction
        fields = ["user_recipe_pk", "step", "text", "image"]
        extra_kwargs = {
            "image": {"required": False},
            "step": {"required": True},
            "text": {"required": True},
        }

    def validate(self, attrs):
        try:
            UserRecipe.objects.get(pk=attrs["user_recipe_pk"])
        except UserRecipe.DoesNotExist:
            raise serializers.ValidationError("Такого рецепта не существует.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        image = validated_data.get("image")
        try:
            recipe = UserRecipe.objects.get(pk=validated_data["user_recipe_pk"])
        except UserRecipe.DoesNotExist:
            raise serializers.ValidationError("Такого рецепта не существует.")
        if image is None:
            image = "img/no_photo.png"
        instruction = Instruction.objects.create(
            user=user,
            step=validated_data["step"],
            text=validated_data["text"],
            image=image,
            recipe_id=recipe.id,
            recipe_title=recipe.title,
        )
        user_recipe = UserRecipe.objects.get(pk=validated_data["user_recipe_pk"])
        user_recipe.instructions.add(instruction)
        return instruction


class EditUserRecipeSerializer(serializers.ModelSerializer):
    user_recipe_pk = serializers.IntegerField(write_only=True, required=True)
    meal_time = serializers.MultipleChoiceField(
        choices=UserRecipe.MEAL_TIME, required=False, write_only=True
    )

    class Meta:
        model = UserRecipe
        fields = [
            "user_recipe_pk",
            "title",
            "description",
            "category",
            "image",
            "type",
            "meal_time",
            "json_products",
            "cooking_time",
        ]
        extra_kwargs = {
            "title": {"required": False, "write_only": True},
            "description": {"required": False, "write_only": True},
            "category": {"required": False, "write_only": True},
            "image": {"required": False, "write_only": True},
            "type": {"required": False, "write_only": True},
            "json_products": {"required": False, "write_only": True, "default": {}},
            "cooking_time": {"required": False, "write_only": True, "default": 0},
        }

    def validate(self, attrs):
        try:
            UserRecipe.objects.get(pk=attrs["user_recipe_pk"])
        except UserRecipe.DoesNotExist:
            raise serializers.ValidationError("Такого рецепта не существует.")
        return attrs

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.category = validated_data.get("category", instance.category)
        instance.image = validated_data.get("image", instance.image)
        instance.type = validated_data.get("type", instance.type)
        instance.meal_time = validated_data.get("meal_time", instance.meal_time)
        instance.json_products = validated_data.get("json_products", instance.json_products)
        instance.cooking_time = validated_data.get("cooking_time", instance.cooking_time)
        instance.update_CPFC()
        instance.save()
        return instance


class DeleteUserRecipeSerializer(serializers.Serializer):
    user_recipe_pk = serializers.IntegerField(write_only=True, required=True)

    def validate(self, attrs):
        try:
            UserRecipe.objects.get(pk=attrs["user_recipe_pk"])
        except UserRecipe.DoesNotExist:
            raise serializers.ValidationError("Такого рецепта не существует.")
        return attrs


class AddOpenRecipeToUserRecipeSerializer(serializers.Serializer):
    open_recipe_pk = serializers.IntegerField(write_only=True, required=True)

    def validate(self, attrs):
        try:
            OpenRecipe.objects.get(pk=attrs["open_recipe_pk"])
        except OpenRecipe.DoesNotExist:
            raise serializers.ValidationError("Такого рецепта не существует.")
        return attrs
