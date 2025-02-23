from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.http import JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt
from django_json_widget.widgets import JSONEditorWidget
from mptt.admin import MPTTModelAdmin

from .forms import RecipeInstructionForm, IngredientForm
from .models.instruction import Instruction
from .models.like import Like
from .models.open_recipe import OpenRecipe
from .models.product import Product
from .models.product_category import ProductCategory
from .models.recipe_category import RecipeCategory
from .models.user_recipe import UserRecipe

import json


@admin.register(OpenRecipe)
class OpenRecipeAdmin(admin.ModelAdmin):
    readonly_fields = [
        "instructions_display",
    ]

    form = RecipeInstructionForm
    change_form_template = "recipes/products_form.html"

    fields = [
        "title",
        "description",
        "category",
        "type",
        "meal_time",
        # "products",
        "json_products",
        "likes",
        "total_views",
        "image",
        ("total_calories", "total_protein", "total_fat", "total_carbohydrates"),
        "cal_100_gram",
        "cooking_time",
        "instructions_display",
        ("instruction", "step"),

    ]

    list_display = [
        "title",
        "update_date",
        "likes",
        "total_views",
        "category",
    ]

    search_fields = [
        "title",
    ]

    sortable_by = ["title", "update_date", "likes", "category"]
    list_filter = ["title", "update_date", "likes", "meal_time", "type", "category"]
    list_per_page = 20

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget(width="50%", height="75%")},
    }

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('add-ingredient/', self.admin_site.admin_view(self.add_ingredient), name='add_ingredient'),
        ]
        return custom_urls + urls

    @method_decorator(csrf_exempt)  # Отключаем CSRF для AJAX-запросов
    def add_ingredient(self, request):
        print(json.loads(request.body))
        """Добавление ингредиента в session через AJAX"""
        if request.method == "POST":
            try:
                data = json.loads(request.body)  # Читаем JSON из запроса
                product_title = data.get("product_title")
                grams = data.get("grams")

                if not product_title or not grams:
                    return JsonResponse({"error": "Некорректные данные"}, status=400)

                ingredient_entry = {
                    "product_title": product_title,
                    "grams": grams,
                }

                if "ingredients" not in request.session:
                    request.session["ingredients"] = []

                request.session["ingredients"].append(ingredient_entry)
                request.session.modified = True

                return JsonResponse({"success": True, "ingredients": request.session["ingredients"]})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)

    def add_view(self, request, form_url='', extra_context=None):
        """Добавляем ingredient_form при создании нового рецепта"""
        if extra_context is None:
            extra_context = {}

        # Инициализируем временный список ингредиентов в сессии
        if 'ingredients' not in request.session:
            request.session['ingredients'] = []

        extra_context['ingredient_form'] = IngredientForm()
        extra_context['added_ingredients'] = request.session.get('ingredients', [])
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
            extra_context['ingredient_form'] = IngredientForm()
        else:
            extra_context['ingredient_form'] = IngredientForm()

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def instructions_display(self, obj):
        instructions = obj.instructions.all()
        return format_html(
            "<br>".join(
                [
                    '<a href="{}">Шаг {}: ID инструкции - {}</a>'.format(
                        reverse("admin:recipes_instruction_change", args=[inst.id]),
                        inst.step,
                        inst.id,
                    )
                    for inst in instructions
                ]
            )
        )

    instructions_display.short_description = "Инструкции к рецепту"

    def save_model(self, request, obj, form, change):
        if "ingredients" in request.session:
            ingredients = request.session["ingredients"]
            ingredients_dict = {item["product_title"]: item["grams"] for item in ingredients}

            if isinstance(obj.json_products, dict):
                obj.json_products.update(ingredients_dict)
            del request.session["ingredients"]
        super().save_model(request, obj, form, change)

        instruction = form.cleaned_data.get("instruction")
        step = form.cleaned_data.get("step")
        step_image = form.cleaned_data.get("step_image")
        recipe_id = obj.id
        recipe_title = obj.title

        if instruction and step:
            recipe_instructions = obj.instructions.filter(step=step)
            if recipe_instructions.exists():
                raise ValidationError(
                    f"Инструкция с шагом {step} уже существует для этого рецепта."
                )

            recipe_instruction = Instruction.objects.create(
                step=step,
                text=instruction,
                image=step_image,
                recipe_id=recipe_id,
                recipe_title=recipe_title,
            )

            obj.instructions.add(recipe_instruction)
            recipe_instruction.recipe_id = obj.id
            recipe_instruction.recipe_title = obj.title
            recipe_instruction.save()

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "products":
    #         kwargs["widget"] = admin.widgets.FilteredSelectMultiple("Продукты", False)
    #         kwargs["widget"].attrs["disabled"] = False
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(RecipeCategory)
class RecipeCategoryAdmin(MPTTModelAdmin):
    list_display = ["title"]
    mptt_level_indent = 20


@admin.register(ProductCategory)
class ProductCategoryAdmin(MPTTModelAdmin):
    list_display = ["title"]
    mptt_level_indent = 20


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
    ]
    search_fields = ["title"]


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    readonly_fields = ["recipe_id", "recipe_title"]
    list_display = ["step", "user", "recipe_title"]
    list_filter = ["user"]


@admin.register(UserRecipe)
class UserRecipeAdmin(admin.ModelAdmin):
    readonly_fields = [
        "instructions_display",
        "pk",
    ]
    change_form_template = "recipes/products_form.html"

    fields = [
        "user",
        "title",
        "description",
        "category",
        "type",
        "meal_time",
        # "products",
        "json_products",
        "image",
        "pk",
        ("total_calories", "total_protein", "total_fat", "total_carbohydrates"),
        "cal_100_gram",
        "instructions_display",
        "cooking_time",
        ("edited", "original_recipe"),
    ]

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget(width="75%", height="50%")},
    }

    list_display = ["title", "user", "edited"]
    list_filter = ["user", "edited"]
    list_per_page = 20

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('add-ingredient/', self.admin_site.admin_view(self.add_ingredient), name='add_ingredient'),
        ]
        return custom_urls + urls

    @method_decorator(csrf_exempt)  # Отключаем CSRF для AJAX-запросов
    def add_ingredient(self, request):
        print(json.loads(request.body))
        """Добавление ингредиента в session через AJAX"""
        if request.method == "POST":
            try:
                data = json.loads(request.body)  # Читаем JSON из запроса
                product_title = data.get("product_title")
                grams = data.get("grams")

                if not product_title or not grams:
                    return JsonResponse({"error": "Некорректные данные"}, status=400)

                ingredient_entry = {
                    "product_title": product_title,
                    "grams": grams,
                }

                if "ingredients" not in request.session:
                    request.session["ingredients"] = []

                request.session["ingredients"].append(ingredient_entry)
                request.session.modified = True

                return JsonResponse({"success": True, "ingredients": request.session["ingredients"]})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)

    def add_view(self, request, form_url='', extra_context=None):
        """Добавляем ingredient_form при создании нового рецепта"""
        if extra_context is None:
            extra_context = {}

        # Инициализируем временный список ингредиентов в сессии
        if 'ingredients' not in request.session:
            request.session['ingredients'] = []

        extra_context['ingredient_form'] = IngredientForm()
        extra_context['added_ingredients'] = request.session.get('ingredients', [])
        return super().add_view(request, form_url, extra_context=extra_context)


    def change_view(self, request, object_id, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
            extra_context['ingredient_form'] = IngredientForm()
        else:
            extra_context['ingredient_form'] = IngredientForm()

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def instructions_display(self, obj):
        instructions = obj.instructions.all()
        return format_html(
            "<br>".join(
                [
                    '<a href="{}">Шаг {}: ID инструкции - {}</a>'.format(
                        reverse("admin:recipes_instruction_change", args=[inst.id]),
                        inst.step,
                        inst.id,
                    )
                    for inst in instructions
                ]
            )
        )

    instructions_display.short_description = "Инструкции к рецепту"
    def save_model(self, request, obj, form, change):
        if "ingredients" in request.session:
            ingredients = request.session["ingredients"]
            ingredients_dict = {item["product_title"]: item["grams"] for item in ingredients}

            if isinstance(obj.json_products, dict):
                obj.json_products.update(ingredients_dict)

            del request.session["ingredients"]
        super().save_model(request, obj, form, change)

        instruction = form.cleaned_data.get("instruction")
        step = form.cleaned_data.get("step")
        step_image = form.cleaned_data.get("step_image")
        recipe_id = obj.id
        recipe_title = obj.title

        if instruction and step:
            recipe_instructions = obj.instructions.filter(step=step)
            if recipe_instructions.exists():
                raise ValidationError(
                    f"Инструкция с шагом {step} уже существует для этого рецепта."
                )

            recipe_instruction = Instruction.objects.create(
                step=step,
                text=instruction,
                image=step_image,
                recipe_id=recipe_id,
                recipe_title=recipe_title,
            )

            obj.instructions.add(recipe_instruction)
            recipe_instruction.recipe_id = obj.id
            recipe_instruction.recipe_title = obj.title
            recipe_instruction.save()

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "products":
    #         kwargs["widget"] = admin.widgets.FilteredSelectMultiple("Продукты", False)
    #         kwargs["widget"].attrs["disabled"] = True
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Like)
class LikeAmdin(admin.ModelAdmin):
    list_display = ["user", "recipe"]
    list_filter = [
        "user",
        "recipe",
    ]
    list_per_page = 20
