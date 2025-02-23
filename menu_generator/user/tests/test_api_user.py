from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TestAPIUser(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_api",
            email="test_api@test.ru",
            password="Test123456",
        )
        self.user.profile.settings = {"product_in": [1, 2], "product_out": [3, 4]}
        self.user.profile.save()
        response = self.client.post(
            reverse("login"),
            data={"login_data": "test_api@test.ru", "password": "Test123456"},
            format="json",
        )
        access_token = f"Q {response.json()['access']}"
        self.client.credentials(HTTP_AUTHORIZATION=access_token)

    def test_get_user(self):
        """Тестируем получение пользователя"""
        response = self.client.get(reverse("get_user"))
        self.assertEqual(response.status_code, 200)
