from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

User = get_user_model()


class SearchHelpersFieldSerializer(serializers.Serializer):
    found_by_recipe_title = serializers.ListField(read_only=True)
    found_by_product = serializers.ListField(read_only=True)
    found_by_product_category = serializers.ListField(read_only=True)

    METHOD_CHOICES = {
        "easy": bool,
        "medium": bool,
        "hard": bool,
    }

    search_method = serializers.ChoiceField(choices=METHOD_CHOICES, write_only=True, required=True)
    user_input = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        user_input = attrs.get("user_input")
        if len(user_input) < 2:
            raise serializers.ValidationError("Строка поиска должна быть не менее 3 символов.")
        return attrs
