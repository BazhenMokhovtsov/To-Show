from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from user.models.profile import Profile
from user.models.user import User


class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_admin", email="test@test.com", password="Test1234"
        )

    def test_get_user(self):
        user = self.user
        profile = self.user.profile

        self.assertEqual(user.username, "test_admin")
        self.assertEqual(user.email, "test@test.com")
        self.assertIsNotNone(profile)
        self.assertEqual(user.pk, profile.pk)

    def test_edit_user(self):
        user = self.user
        user.username = "edit_admin"
        user.save()

        self.assertEqual(user.username, "edit_admin")

        user.profile.settings = {"product_in": [1, 2]}

        user.profile.save()
        self.assertIsNotNone(user.profile.settings)

    def test_delete_user(self):
        user = self.user
        user.delete()

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
