import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from myapp.models import ProAccount, Service
from django.conf import settings

# pylint: disable=no-member


class DashboardViewsTest(TestCase):
    def setUp(self):
        """
        Setup the test environment with a test user and pro account.
        """
        # Ensure 'testserver' is in ALLOWED_HOSTS during tests
        settings.ALLOWED_HOSTS.append("testserver")

        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )

        # Create a ProAccount for the test user
        self.pro_account = ProAccount.objects.create(
            user=self.user, business_name="Test Business"
        )

        # Create a test client and login as the test user
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        # Create a test service for testing services update
        self.service = Service.objects.create(
            name="Test Service", category="Test Category"
        )

    def tearDown(self):
        """
        Clean up after each test by deleting the user, pro account, and service.
        """
        self.service.delete()
        self.pro_account.delete()
        self.user.delete()

    def test_dashboard_redirect_if_not_pro(self):
        """
        Test if a user without a pro account is redirected to the "become a pro" page.
        """
        # Create a non-pro user
        non_pro_user = get_user_model().objects.create_user(
            username="nonpro",
            password="testpassword",
            email="nonpro@example.com",
            first_name="Jane",
            last_name="Doe",
        )
        self.client.login(username="nonpro", password="testpassword")

        response = self.client.get(reverse("dashboard"))

        # Check for redirection to the "become a pro" page
        self.assertRedirects(response, reverse("become_a_pro"))

        # Clean up
        non_pro_user.delete()

    def test_update_business_name(self):
        """
        Test updating the business name via POST request.
        """
        url = reverse("update_business_name")
        data = json.dumps({"business_name": "New Business Name"})
        response = self.client.post(url, data, content_type="application/json")

        # Check for successful update
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # Verify that the business name was updated
        self.pro_account.refresh_from_db()
        self.assertEqual(self.pro_account.business_name, "New Business Name")

    def test_update_business_name_empty(self):
        """
        Test updating the business name with an empty string, expecting it to be set to None.
        """
        url = reverse("update_business_name")
        data = json.dumps({"business_name": ""})
        response = self.client.post(url, data, content_type="application/json")

        # Check for successful update
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # Verify that the business name is set to None
        self.pro_account.refresh_from_db()
        self.assertIsNone(self.pro_account.business_name)

    def test_update_business_name_invalid_json(self):
        """
        Test updating the business name with invalid JSON.
        """
        url = reverse("update_business_name")
        data = "invalid json string"
        response = self.client.post(url, data, content_type="application/json")

        # Check for error in response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "success": False,
                "error": "Expecting value: line 1 column 1 (char 0)",
            },
        )

    def test_update_services(self):
        """
        Test updating the services offered by the pro account.
        """
        url = reverse("update_services")
        data = json.dumps({"services": [self.service.id]})
        response = self.client.post(url, data, content_type="application/json")

        # Check for successful update
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # Verify that the service is associated with the pro account
        self.pro_account.refresh_from_db()
        self.assertIn(self.service, self.pro_account.services.all())

    def test_update_services_invalid_service(self):
        """
        Test updating services with an invalid service ID.
        """
        url = reverse("update_services")
        data = json.dumps({"services": [999]})  # Invalid service ID
        response = self.client.post(url, data, content_type="application/json")

        # Check for bad request due to invalid service
        self.assertEqual(
            response.status_code, 400
        )  # Bad request or validation error expected

    def test_update_phone_number(self):
        """
        Test updating the phone number.
        """
        url = reverse("update_phone_number")
        data = json.dumps({"phone_number": "123-456-7890"})
        response = self.client.post(url, data, content_type="application/json")

        # Check for successful update
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # Verify that the phone number was updated
        self.pro_account.refresh_from_db()
        self.assertEqual(self.pro_account.phone_number, "123-456-7890")

    def test_upload_profile_picture_invalid_method(self):
        """
        Test uploading a profile picture using a GET request instead of POST.
        """
        url = reverse("upload_profile_picture_dashboard")
        response = self.client.get(url)

        # Check for method not allowed (405)
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_update_profile_visibility(self):
        """
        Test updating profile visibility.
        """
        url = reverse("update_profile_visibility")
        data = json.dumps({"profile_visibility": True})
        response = self.client.post(url, data, content_type="application/json")

        # Check for successful update
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # Verify that the profile visibility was updated
        self.pro_account.refresh_from_db()
        self.assertTrue(self.pro_account.profile_visibility)

    def test_get_user_profile_pic(self):
        """
        Test retrieving the user's profile picture URL.
        """
        url = reverse("get_user_profile_pic")
        response = self.client.get(url)

        # Check for successful response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content, {"profile_pic_url": None}
        )  # No picture uploaded yet
