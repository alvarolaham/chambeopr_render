import os
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase


class UserCreationDuplicateTest(TestCase):
    def setUp(self):
        User = get_user_model()
        password = os.getenv("TEST_USER_PASSWORD", "defaultpassword")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=password,
            first_name="Test",
            last_name="User",
        )

    def test_duplicate_username(self):
        print(
            "Testing if a user cannot be created with a duplicate username..."
        )
        User = get_user_model()
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="testuser",
                email="newemail@example.com",
                password="anotherpassword",
                first_name="Test",
                last_name="User",
            )
        print("Test passed: Duplicate username was not allowed.\n")

    def test_duplicate_email(self):
        print("Testing if a user cannot be created with a duplicate email...")
        User = get_user_model()
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="newuser",
                email="test@example.com",
                password="anotherpassword",
                first_name="Test",
                last_name="User",
            )
        print("Test passed: Duplicate email was not allowed.\n")
