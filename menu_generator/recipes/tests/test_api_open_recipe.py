from django.contrib.auth import get_user_model
from django.urls import reverse
from recipes.models.instruction import Instruction
from recipes.models.like import Like
from recipes.models.open_recipe import OpenRecipe
from recipes.models.product import Product
from recipes.models.product_category import ProductCategory
from recipes.models.recipe_category import RecipeCategory
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class OpenRecipeAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="Testpassword123",
            email="test@test.com",
        )

        self.client.force_authenticate(user=self.user)

        self.recipe_category = RecipeCategory.objects.create(title="test_category")
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

        self.open_recipe = OpenRecipe.objects.create(
            title="test_user_recipe",
            description="test_description",
            category=self.recipe_category,
            type="hot",
            meal_time=["breakfast"],
        )

    def test_get_all_open_recipes(self):
        url = reverse("get_all_open_recipes")
        response = self.client.get(url)

        self.assertIn("detail", response.json())
        self.assertEqual(response.status_code, 200)

    def test_get_open_recipe(self):
        url = reverse("get_open_recipe")
        data = {"open_recipe_pk": self.open_recipe.pk}
        response = self.client.post(url, data=data, format="json")

        self.assertIn("detail", response.json())
        self.assertEqual(response.status_code, 200)

    def test_set_like_and_remove_on_the_second_installation(self):
        url = reverse("set_like")
        data = {
            "open_recipe_pk": self.open_recipe.pk,
        }
        response = self.client.post(url, data=data, format="json")
        self.open_recipe.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Like.objects.filter(recipe=self.open_recipe).count(), 1)
        self.assertEqual(self.open_recipe.likes, 1)

        self.client.post(url, data=data, format="json")
        self.open_recipe.refresh_from_db()

        self.assertEqual(Like.objects.filter(recipe=self.open_recipe).count(), 0)
        self.assertEqual(self.open_recipe.likes, 0)
