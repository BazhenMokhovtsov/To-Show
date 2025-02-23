from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TestAPIAuth(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.refresh_url = reverse("refresh")
        self.user = User.objects.create_user(
            username="test_auth", email="user@test.com", password="Test123456"
        )

    def test_login_valid_data(self):
        """Тестируем вход с правильными данными"""
        user_data = {"login_data": "test_auth", "password": "Test123456"}
        response = self.client.post(self.login_url, data=user_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

        user_data.update({"login": "user@test.com"})
        response = self.client.post(self.login_url, data=user_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_login_invalid_login(self):
        user_data = {"login_data": "invalid_user", "password": "Test123456"}
        response = self.client.post(self.login_url, data=user_data, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Неверный логин или пароль.", response.json()["detail"])

    def test_login_invalid_password(self):
        user_data = {"login_data": "test_user", "password": "test123456"}
        response = self.client.post(self.login_url, data=user_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Пароль должен содержать хотя бы одну заглавную букву.",
            response.json()["non_field_errors"][0],
        )

        user_data = {"login_data": "test_user", "password": "test6"}
        response = self.client.post(self.login_url, data=user_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Пароль должен быть не менее 8 символов.",
            response.json()["non_field_errors"][0],
        )

        user_data = {"login_data": "test_user", "password": "12345678"}
        response = self.client.post(self.login_url, data=user_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Пароль должен содержать и буквы и цифры.",
            response.json()["non_field_errors"][0],
        )

    def test_logout(self):
        user_data = {"login_data": "test_auth", "password": "Test123456"}
        response = self.client.post(self.login_url, data=user_data, format="json")
        self.assertEqual(response.status_code, 200)

        access_token = response.json()["access"]
        refresh_token = response.json()["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Q {access_token}")

        data = {"refresh": refresh_token}
        response = self.client.post(self.logout_url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Вы вышли из системы.", response.json()["detail"])

        response = self.client.post(self.logout_url, data=data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_refresh(self):
        user_data = {"login_data": "test_auth", "password": "Test123456"}
        response = self.client.post(self.login_url, data=user_data, format="json")
        self.assertEqual(response.status_code, 200)

        access_token = response.json()["access"]
        refresh_token = response.json()["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Q {access_token}")

        data = {"refresh": refresh_token}
        response = self.client.post(self.refresh_url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

        response = self.client.post(self.logout_url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
