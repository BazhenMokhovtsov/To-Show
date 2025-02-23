from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TestAPIEditUser(APITestCase):

    def setUp(self):
        self.change_email_first_step = reverse("change_email_first_step")
        self.change_email_second_step = reverse("change_email_second_step")
        self.change_password = reverse("change_password")
        self.delete_account = reverse("delete_account")
        self.edit_user = reverse("edit_user")
        self.user = User.objects.create_user(
            username="test_edit", email="edit@test.com", password="Test123456"
        )
        self.client = APIClient()
        response = self.client.post(
            reverse("login"),
            data={"login_data": "test_edit", "password": "Test123456"},
            format="json",
        )
        access_token = f"Q {response.json()['access']}"
        self.client.credentials(HTTP_AUTHORIZATION=access_token)

    def test_change_email_first_step_valid_data(self):
        """Тестируем первый шаг с правильными данными"""
        user_data = {
            "email": "edit1@test.com",
        }
        response = self.client.post(self.change_email_first_step, data=user_data, format="json")
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertIn("change_email", session)

    def test_change_email_first_step_invalid_email(self):
        """Тестируем первый шаг с неправильной почтой"""
        user_data = {
            "email": "test_edit",
        }
        response = self.client.post(self.change_email_first_step, data=user_data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_change_email_first_step_already_exist_email(self):
        """Тестируем первый шаг с существующим пользователем"""
        user_data = {
            "email": "edit@test.com",
        }
        response = self.client.post(self.change_email_first_step, data=user_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())

    def test_change_email_second_step_valid_data(self):
        """Тестируем второй шаг с правильными данными"""
        self.test_change_email_first_step_valid_data()
        session = self.client.session
        user_data = session["change_email"]
        user_data = {
            "code": user_data["code"],
        }
        response = self.client.post(self.change_email_second_step, data=user_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(pk=self.user.pk).email, "edit1@test.com")
        self.assertNotIn("change_email", self.client.session)

    def test_change_email_second_step_invalid_code(self):
        """Тестируем второй шаг с неправильным кодом"""
        self.test_change_email_first_step_valid_data()
        user_data = {
            "code": "12345",
        }
        response = self.client.post(self.change_email_second_step, data=user_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_change_password_valid_data(self):
        """Тестируем смену пароля с правильными данными"""
        data = {
            "old_password": "Test123456",
            "new_password": "Test1234567",
            "confirm_password": "Test1234567",
        }
        response = self.client.post(self.change_password, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.json())

    def test_change_password_invalid_new_password(self):
        """Тестируем смену пароля с неправильным новым паролем"""
        data = {
            "old_password": "Test123456",
            "new_password": "Test12345",
            "confirm_password": "Test1234567",
        }
        response = self.client.post(self.change_password, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Новые пароли не совпадают", response.json()["non_field_errors"][0])

        data.update({"new_password": "test1234567", "confirm_password": "test1234567"})
        response = self.client.post(self.change_password, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Новый пароль должен содержать хотя бы одну заглавную букву",
            response.json()["non_field_errors"][0],
        )

    def test_change_password_invalid_confirm_password(self):
        """Тестируем смену пароля с неправильным подтверждением пароля"""
        data = {
            "old_password": "Test123456",
            "new_password": "Test1234567",
            "confirm_password": "Test12345",
        }
        response = self.client.post(self.change_password, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Новые пароли не совпадают", response.json()["non_field_errors"][0])

        data.update({"confirm_password": "12345678"})
        response = self.client.post(self.change_password, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Новые пароли не совпадают", response.json()["non_field_errors"][0])

        data.update({"confirm_password": "12345678", "new_password": "12345678"})
        response = self.client.post(self.change_password, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Новый пароль должен содержать и буквы и цифры",
            response.json()["non_field_errors"][0],
        )

    def test_delete_account(self):
        """Тестируем удаление аккаунта"""
        user = User.objects.create_user(
            username="test_delete", email="delete@test.com", password="Test123456"
        )
        response = self.client.post(
            reverse("login"),
            data={"login_data": "test_delete", "password": "Test123456"},
            format="json",
        )
        access_token = f'Q {response.json()["access"]}'
        self.client.credentials(HTTP_AUTHORIZATION=access_token)
        response = self.client.get(self.delete_account)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(User.objects.filter(username="test_delete").first())

    def test_edit_user(self):
        """Тестируем редактирование пользователя"""
        image_file = SimpleUploadedFile(
            name="no_photo.png",
            content=open("static/img/no_photo.png", "rb").read(),
            content_type="image/png",
        )
        user_data = {"username": "test_edit_after", "image": image_file}
        response = self.client.post(
            self.edit_user,
            data=user_data,
            format="multipart",
            enctype="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="test_edit_after")
        self.assertEqual(user.username, "test_edit_after")

        user_data = {"username": "test_edit_after1"}
        response = self.client.post(
            self.edit_user,
            data=user_data,
            format="multipart",
            enctype="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)

        image_file = SimpleUploadedFile(
            name="no_photo.png",
            content=open("static/img/no_photo.png", "rb").read(),
            content_type="image/png",
        )
        user_data = {"image": image_file}
        response = self.client.post(
            self.edit_user,
            data=user_data,
            format="multipart",
            enctype="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
