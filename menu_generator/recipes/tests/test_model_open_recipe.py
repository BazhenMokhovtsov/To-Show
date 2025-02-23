from django.contrib.auth import get_user_model
from django.test import TestCase
from recipes.models.instruction import Instruction
from recipes.models.product import Product
from recipes.models.product_category import ProductCategory
from recipes.models.recipe_category import RecipeCategory
from recipes.models.user_recipe import OpenRecipe

User = get_user_model()


class TestOpenRecipeModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            email="test_user@test.ru",
            password="Test123456",
        )

        self.recipe_category = RecipeCategory.objects.create(title="test_category", parent=None)
        self.product_category = ProductCategory.objects.create(title="test_category", parent=None)
        for number in range(1, 3):
            setattr(
                self,
                f"product_{number}",
                Product.objects.create(
                    title=f"test_product_{number}",
                    category=self.product_category,
                    brutto="grams",
                    calories=100,
                    protein=100,
                    fat=100,
                    carbohydrates=100,
                ),
            )

        self.instruction_1 = Instruction.objects.create(
            user=self.user,
            text="instruction_text_1",
            step=1,
        )

    def test_create_open_recipe(self):
        self.open_recipe = OpenRecipe.objects.create(
            title="test_open_recipe",
            description="test_description",
            category=self.recipe_category,
            type="hot",
            meal_time=["breakfast"],
            json_products={"test_product_1": 100, "test_product_2": 100},
        )

        self.open_recipe.instructions.add(self.instruction_1)

        self.assertEqual(self.open_recipe.instructions.all().count(), 1)
        self.assertEqual(self.open_recipe.products.all().count(), 2)
        self.assertEqual(self.open_recipe.total_calories, 200)

    def test_create_open_recipe_products_uppercase(self):
        self.open_recipe = OpenRecipe.objects.create(
            title="test_open_recipe_1",
            description="test_description",
            category=self.recipe_category,
            type="hot",
            meal_time=["breakfast"],
            json_products={"Test_product_1": 100, "Test_product_2": 100},
        )

        self.open_recipe.instructions.add(self.instruction_1)

        self.assertEqual(self.open_recipe.instructions.all().count(), 1)
        self.assertEqual(self.open_recipe.products.all().count(), 2)
        self.assertEqual(self.open_recipe.total_calories, 200)

        self.open_recipe = OpenRecipe.objects.create(
            title="test_open_recipe_2",
            description="test_description",
            category=self.recipe_category,
            type="hot",
            meal_time=["breakfast"],
            json_products={"test_product_1": 100, "test_product_2": 100},
        )

        self.open_recipe.instructions.add(self.instruction_1)

        self.assertEqual(self.open_recipe.instructions.all().count(), 1)
        self.assertEqual(self.open_recipe.products.all().count(), 2)
        self.assertEqual(self.open_recipe.total_calories, 200)
