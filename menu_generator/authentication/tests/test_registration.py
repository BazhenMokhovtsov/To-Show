import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TestAPIRegistration(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.first_step_url = reverse("registration_first_step")
        self.second_step_url = reverse("registration_second_step")

    def test_first_step_valid_data(self):
        """Тестируем правильные введенные данные."""
        data = {
            "username": "test_user",
            "email": "test@test.com",
            "password": "Test1234",
            "password_confirm": "Test1234",
        }
        response = self.client.post(self.first_step_url, data=data, format="json")

        self.assertEqual(response.status_code, 200)

        code = response.json()["detail"].split(" ")[-1]
        print(response.json())
        session = self.client.session
        session["user_data"] = {
            "username": data["username"],
            "email": data["email"],
            "password": data["password"],
            "code": code,
            "expired_at": datetime.datetime.now() + datetime.timedelta(minutes=5),
        }
        session.save()

    def test_first_step_invalid_data(self):
        """Тестируем неправильные введенные данные."""
        data = {
            "username": 1,
            "email": "test@test.com",
            "password": "Test1234",
            "password_confirm": "Test1234",
        }
        response = self.client.post(self.first_step_url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Имя пользователя" in response.json()["non_field_errors"][0])

        data = data.update({"username": "test_user", "email": "testtest.com"})
        response = self.client.post(self.first_step_url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())

    def test_first_step_invalid_password(self):
        """Тестируем неправильно введенный пароль"""
        data = {
            "username": "test_user",
            "email": "test@test.com",
            "password": "1234",
            "password_confirm": "Test1234",
        }
        response = self.client.post(self.first_step_url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertTrue("Пароли не совпадают." in response.json()["non_field_errors"][0])

        data.update(
            {
                "password": "test1234",
                "password_confirm": "test1234",
            }
        )
        response = self.client.post(self.first_step_url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertTrue("заглавную букву." in response.json()["non_field_errors"][0])

        data.update(
            {
                "password": "Test@123456",
                "password_confirm": "Test@123456",
            }
        )
        response = self.client.post(self.first_step_url, data, format="json")
        self.assertEqual(response.status_code, 400)

        data.update(
            {
                "password": "Test 123456",
                "password_confirm": "Test 123456",
            }
        )
        response = self.client.post(self.first_step_url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_second_step_valid_data(self):
        """Тестируем правильные введенные данные."""
        self.test_first_step_valid_data()
        user_data = self.client.session["user_data"]
        data = {
            "code": user_data["code"],
        }
        response = self.client.post(self.second_step_url, data=data, format="json")

        self.assertEqual(response.status_code, 200)

    def test_second_step_invalid_code(self):
        """Тестируем неправильные введенные код."""
        self.test_first_step_valid_data()
        data = {
            "code": "123456",
        }
        response = self.client.post(self.second_step_url, data=data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_second_step_bad_time_code(self):
        """Тестируем истекшее время кода"""
        self.test_first_step_valid_data()
        session = self.client.session
        session["user_data"]["expired_at"] = datetime.datetime.now() - datetime.timedelta(
            minutes=10
        )
        session.save()
        data = {
            "code": self.client.session["user_data"]["code"],
        }
        response = self.client.post(self.second_step_url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
