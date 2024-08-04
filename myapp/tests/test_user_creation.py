"""
This is test_user_creation.py
"""

import os

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase


class UserCreationTest(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'myapp_myuser'"
            )
            columns = cursor.fetchall()
            print("MyUser table structure:")
            for column in columns:
                print(f"{column[0]}: {column[1]}")

    def __str__(self):
        return self._testMethodName.replace("_", " ").capitalize()

    def test_create_user(self):
        print("Testing if a user can be created with valid details...")
        User = get_user_model()
        password = os.getenv("TEST_USER_PASSWORD", "defaultpassword")
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=password,
            first_name="Test",
            last_name="User",
        )
        print("User created successfully. Verifying user details...")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_pro)
        print("User details verified successfully.\n")
