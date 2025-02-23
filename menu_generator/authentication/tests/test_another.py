import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TestAPIAnother(APITestCase):

    def setUp(self):
        self.remember_password_first_step = reverse("remember_password_first_step")
        self.remember_password_second_step = reverse("remember_password_second_step")
        self.remember_password_set_password = reverse("remember_password_set_password")
        self.user = User.objects.create_user(
            username="test_another", email="another@test.com", password="Test123456"
        )

    def test_first_step_valid_data(self):
        """Тестируем первый шаг с правильными данными"""
        user_data = {
            "login_data": "test_another",
        }
        response = self.client.post(
            self.remember_password_first_step, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 200)

        user_data.update({"login_data": "another@test.com"})
        response = self.client.post(
            self.remember_password_first_step, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_first_step_invalid_login(self):
        """Тестируем первый шаг с неправильными данными"""
        user_data = {"login_data": ["idk"]}
        response = self.client.post(
            self.remember_password_first_step, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_first_step_not_found_user(self):
        """Тестируем первый шаг с несуществующим пользователем"""
        user_data = {"login_data": "not_found_user"}
        response = self.client.post(
            self.remember_password_first_step, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Пользователь не найден", response.json()["detail"])

    def test_second_step_valid_data(self):
        """Тестируем второй шаг с правильными данными"""
        self.test_first_step_valid_data()
        code = self.client.session["user_data"]["code"]
        user_data = {"code": code}
        response = self.client.post(
            self.remember_password_second_step, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_second_step_invalid_code(self):
        """Тестируем второй шаг с неправильными кодом"""
        self.test_first_step_valid_data()
        user_data = {"code": "123456"}
        response = self.client.post(
            self.remember_password_second_step, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Неверный код", response.json()["detail"])

    def test_second_step_bad_time_code(self):
        """Тестируем второй шаг с истекшим временем кода"""
        self.test_first_step_valid_data()
        session = self.client.session
        session["user_data"]["expired_at"] = datetime.datetime.now() - datetime.timedelta(
            minutes=10
        )
        session.save()
        code = self.client.session["user_data"]["code"]
        user_data = {"code": code}
        response = self.client.post(
            self.remember_password_second_step, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Срок действия кода истек", response.json()["detail"])

    def test_set_password_valid_data(self):
        """Тестируем установку пароля с правильными данными"""
        self.test_first_step_valid_data()
        user_data = {"password": "Newtest123", "confirm_password": "Newtest123"}
        response = self.client.post(
            self.remember_password_set_password, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Пользователь успешно изменил пароль", response.json()["detail"])

        session = self.client.session
        self.assertNotIn("user_data", session)

    def test_set_password_invalid_password(self):
        self.test_first_step_valid_data()
        user_data = {"password": "12234566", "confirm_password": "12234566"}
        response = self.client.post(
            self.remember_password_set_password, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Пароль должен содержать и буквы и цифры.",
            response.json()["non_field_errors"][0],
        )

        user_data.update({"password": "newtest123", "confirm_password": "newtest123"})
        response = self.client.post(
            self.remember_password_set_password, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Пароль должен содержать хотя бы одну заглавную букву.",
            response.json()["non_field_errors"][0],
        )

        user_data.update({"password": "Test1234444", "confirm_password": "Newtest123"})
        response = self.client.post(
            self.remember_password_set_password, data=user_data, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Пароли не совпадают", response.json()["non_field_errors"][0])
