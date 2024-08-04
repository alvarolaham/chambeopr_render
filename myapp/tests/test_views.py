"""
This is test_views.py
"""

import os

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CustomUserCreationForm


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    ALLOWED_HOSTS=["testserver"],
)
class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse("index")
        self.signup_url = reverse("signup")
        self.User = get_user_model()
        self.test_password = os.getenv("TEST_USER_PASSWORD", "Secure123!@#")

    def __str__(self):
        return self._testMethodName.replace("_", " ").capitalize()

    def test_index_page_loads_successfully(self):
        print("Testing if the index page loads successfully...")
        response = self.client.get(self.index_url)
        print(f"Index GET response status code: {response.status_code}")
        self.assertEquals(response.status_code, 200)
        print("Index page loaded successfully.\n")

    def test_signup_page_loads_successfully(self):
        print("Testing if the signup page loads successfully...")
        response = self.client.get(self.signup_url)
        print(f"Signup GET response status code: {response.status_code}")
        self.assertEquals(response.status_code, 200)
        if response.context is not None:
            self.assertIsInstance(
                response.context["form"], CustomUserCreationForm
            )
            print("Signup page loaded successfully with form in context.\n")
        else:
            print("No context available.\n")

    def test_user_can_signup_with_valid_data(self):
        print("Testing if a user can sign up with valid data...")
        response = self.client.post(
            self.signup_url,
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": self.test_password,
                "password2": self.test_password,
                "first_name": "John",
                "last_name": "Doe",
            },
        )
        print(
            f"Signup POST valid data response status code: {response.status_code}"
        )
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        user = self.User.objects.filter(username="testuser").first()
        self.assertIsNotNone(user)
        print(f"User created: {user}")
        print(f"User fields: {user.__dict__}")
        print("User signed up successfully with valid data.\n")

    def test_signup_fails_with_invalid_data(self):
        print("Testing if the signup fails with invalid data...")
        response = self.client.post(
            self.signup_url,
            {
                "username": "",
                "email": "invalid_email",
                "password1": "short",
                "password2": "different",
            },
        )
        print(
            f"Signup POST invalid data response status code: {response.status_code}"
        )
        self.assertEquals(response.status_code, 200)
        if response.context is not None and "form" in response.context:
            print(f"Form errors: {response.context['form'].errors}")
            self.assertIn(
                "This field is required.",
                response.context["form"].errors.get("username", []),
            )
            self.assertIn(
                "Enter a valid email address.",
                response.context["form"].errors.get("email", []),
            )
            self.assertIn(
                "This password is too short. It must contain at least 8 characters.",
                response.context["form"].errors.get("password1", []),
            )
            self.assertIn(
                "The two password fields didn’t match.",
                response.context["form"].errors.get("password2", []),
            )
            print("Signup failed with invalid data as expected.\n")
        else:
            print("No context or form available.\n")
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)
        self.assertFalse(self.User.objects.filter(username="").exists())
