from django.contrib.auth import get_user_model
from django.test import TestCase
from recipes.models.instruction import Instruction
from recipes.models.open_recipe import OpenRecipe
from recipes.models.product import Product
from recipes.models.product_category import ProductCategory
from recipes.models.recipe_category import RecipeCategory
from recipes.models.user_recipe import UserRecipe

User = get_user_model()


class TestUserRecipeModel(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser",
            email="testmodel@test.ru",
            password="Test123456",
        )
        ProductCategory.objects.create(title="test_category", parent=None)
        products = ["test_product_1", "test_product_2"]
        for product in products:
            Product.objects.create(
                title=product,
                category=ProductCategory.objects.get(title="test_category"),
                brutto="grams",
                calories=100,
                protein=100,
                fat=100,
                carbohydrates=100,
            )

    def test_create_user_recipe(self):
        user_recipe = UserRecipe.objects.create(
            user=self.user,
            title="test_user_recipe",
            description="test_description",
            category=RecipeCategory.objects.create(title="test_category", parent=None),
            type="hot",
            meal_time="breakfast",
            edited=False,
            original_recipe=None,
        )
        self.assertEqual(user_recipe.title, "test_user_recipe")
        self.assertEqual(user_recipe.pk, UserRecipe.objects.get(pk=user_recipe.pk).pk)

    def test_edit_user_recipe(self):
        user_recipe = UserRecipe.objects.create(
            user=self.user,
            title="test_user_recipe",
            description="test_description",
            category=RecipeCategory.objects.create(title="test_category", parent=None),
            type="hot",
            meal_time="breakfast",
            edited=False,
            original_recipe=None,
            json_products={},
        )
        self.assertIsNotNone(UserRecipe.objects.get(pk=user_recipe.pk))

        user_recipe.title = "edit_test_user_recipe"
        for product in Product.objects.all():
            user_recipe.products.add(product)
        user_recipe.save()

        self.assertEqual(user_recipe.title, "edit_test_user_recipe")
        self.assertEqual(user_recipe.pk, UserRecipe.objects.get(pk=user_recipe.pk).pk)
        self.assertIsNotNone(user_recipe.products.all())
        self.assertIsNotNone(user_recipe.image)

        steps_instruction = range(1, 5)
        for step in steps_instruction:
            inst = Instruction.objects.create(
                user=self.user, text=f"test use insctruction {step}", step=step
            )
            user_recipe.instructions.add(inst)
        user_recipe.save()
        self.assertIsNotNone(user_recipe.instructions.all())

        user_recipe.meal_time = ["dinner", "breakfast"]
        user_recipe.save()
        self.assertEqual(len(user_recipe.meal_time), 2)

        crfc = []
        for position in [
            user_recipe.total_calories,
            user_recipe.total_protein,
            user_recipe.total_fat,
            user_recipe.total_carbohydrates,
        ]:
            crfc.append(position)
        self.assertEqual(crfc[0], sum([product.calories for product in user_recipe.products.all()]))

        user_recipe.edited = True
        open_recipe = OpenRecipe.objects.create(
            title="test_open_recipe",
            description="test_description",
            category=RecipeCategory.objects.create(title="test_category_1", parent=None),
            type="hot",
            meal_time="breakfast",
        )
        user_recipe.original_recipe = open_recipe
        user_recipe.save()
        self.assertEqual(user_recipe.edited, True)
        self.assertIsNotNone(user_recipe.original_recipe)

    def test_delete_user_recipe(self):
        user_recipe = UserRecipe.objects.create(
            user=self.user,
            title="test_user_recipe",
            description="test_description",
            category=RecipeCategory.objects.create(title="test_category_2", parent=None),
            type="hot",
            meal_time="breakfast",
            edited=False,
            original_recipe=None,
        )
        self.assertIsNotNone(UserRecipe.objects.get(pk=user_recipe.pk))
        user_recipe.delete()
        self.assertEqual(UserRecipe.objects.all().count(), 0)
