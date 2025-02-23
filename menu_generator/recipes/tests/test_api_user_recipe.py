from django.contrib.auth import get_user_model
from django.urls import reverse
from recipes.models.instruction import Instruction
from recipes.models.open_recipe import OpenRecipe
from recipes.models.product import Product
from recipes.models.product_category import ProductCategory
from recipes.models.recipe_category import RecipeCategory
from recipes.models.user_recipe import UserRecipe
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TestAPIUserRecipe(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_api",
            email="test_api@test.ru",
            password="Test123456",
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("login"),
            data={"login_data": "test_api", "password": "Test123456"},
            format="json",
        )
        access_token = f'Q {response.json()["access"]}'
        self.client.credentials(HTTP_AUTHORIZATION=access_token)
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
        self.user_recipe = UserRecipe.objects.create(
            user=self.user,
            title="test_user_recipe",
            description="test_description",
            category=self.recipe_category,
            type="hot",
            meal_time=["breakfast"],
            edited=False,
            original_recipe=None,
        )

    def test_list_auth_user_recipe(self):
        url = reverse("list_auth_user_recipes")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.json())

    def test_create_user_recipe_valid_data(self):
        url = reverse("create_user_recipe")
        data = {
            "title": "test_create_user_recipe",
            "description": "test_description",
            "category": self.recipe_category.pk,
            "type": "hot",
            "meal_time": ["breakfast"],
            "json_products": {
                "test_product_1": 100,
                "test_product_2": 100,
            },
            "edited": False,
            "original_recipe": None,
        }
        response = self.client.post(url, data=data, format="json")
        user_recipe_pk = response.json()["detail"]["id"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(UserRecipe.objects.get(pk=user_recipe_pk).products.count(), 2)

    def test_create_user_recipe_with_multiplechoice_meal_time(self):
        url = reverse("create_user_recipe")
        data = {
            "title": "test_create_user_recipe",
            "description": "test_description",
            "category": self.recipe_category.pk,
            "type": "hot",
            "meal_time": ["breakfast", "dinner"],
            "products": [self.product_1.pk, self.product_2.pk],
            "edited": False,
            "original_recipe": None,
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_get_user_recipe(self):
        url = reverse("get_user_recipe")
        data = {"user_recipe_pk": self.user_recipe.pk}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.json())

    def test_add_instructions_to_user_recipe(self):
        url = reverse("add_instruction_for_user_recipe")
        data = {"user_recipe_pk": self.user_recipe.pk, "step": 1, "text": "test_text"}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("detail", response.json())

    def test_edit_user_recipe_valid_data(self):
        url = reverse("edit_user_recipe")
        data = {
            "user_recipe_pk": self.user_recipe.pk,
            "title": "test_edit_user_recipe",
            "description": "test_description",
            "category": self.recipe_category.pk,
            "type": "snacks",
            "meal_time": ["dinner"],
            "products": [self.product_1.pk],
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 202)

    def test_edit_user_recipe_invalid_category(self):
        url = reverse("edit_user_recipe")
        data = {
            "user_recipe_pk": self.user_recipe.pk,
            "title": "test_edit_user_recipe",
            "description": "test_description",
            "category": 100,
            "type": "snacks",
            "meal_time": ["dinner"],
            "products": [self.product_2.pk],
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("category", response.json())

    def test_edit_user_recipe_invalid_user_recipe_pk(self):
        url = reverse("edit_user_recipe")
        data = {
            "user_recipe_pk": 100,
            "title": "test_edit_user_recipe",
            "description": "test_description",
            "category": self.recipe_category.pk,
            "type": "snacks",
            "meal_time": ["dinner"],
            "products": [self.product_1.pk],
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.json())

    def test_edit_user_recipe_valid_short_data(self):
        url = reverse("edit_user_recipe")
        data = {
            "user_recipe_pk": self.user_recipe.pk,
            "description": "test_edit_user_recipe",
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 202)

    def test_delete_user_recipe(self):
        url = reverse("delete_user_recipe")
        data = {"user_recipe_pk": self.user_recipe.pk}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 204)

    def test_delete_user_recipe_check_instruction(self):
        url = reverse("add_instruction_for_user_recipe")
        for number in range(1, 3):
            data = {
                "user_recipe_pk": self.user_recipe.pk,
                "step": number,
                "text": "test_text",
            }
            response = self.client.post(url, data=data, format="json")

        url = reverse("delete_user_recipe")
        data = {"user_recipe_pk": self.user_recipe.pk}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 204)

    def test_add_open_recipe_to_user_recipe(self):
        url = reverse("add_open_recipe_to_user_recipe")
        open_recipe_test = OpenRecipe.objects.create(
            title="test_open_recipe",
            description="test_description",
            category=self.recipe_category,
            type="hot",
            meal_time="dinner",
        )
        open_recipe_test.products.add(self.product_1)
        data = {"open_recipe_pk": open_recipe_test.pk}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(UserRecipe.objects.filter(original_recipe=open_recipe_test).count(), 1)
