import json
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from .models import ProAccount, UserProfile

UserModel = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = UserModel
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if UserModel.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose a different one."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists. Please use a different email address."
            )
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        first_name = (
            self.cleaned_data.get("first_name") or ""
        )  # Ensure it’s not None
        last_name = (
            self.cleaned_data.get("last_name") or ""
        )  # Ensure it’s not None
        username = (
            self.cleaned_data.get("username") or ""
        )  # Ensure it’s not None

        if password1 != password2:
            raise forms.ValidationError("The two password fields must match.")

        # Ensure none of the fields are None before using lower() method
        if any(
            item.lower() in password1.lower()
            for item in [first_name, last_name, username]
            if item
        ):
            raise forms.ValidationError(
                "The password should not contain your first name, last name, or username."
            )

        return password2


class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        required=True,
        help_text="Enter the 6-digit code sent to your email.",
    )


class CustomSetPasswordForm(SetPasswordForm):
    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        first_name = self.user.first_name or ""  # Ensure it’s not None
        last_name = self.user.last_name or ""  # Ensure it’s not None
        username = self.user.username or ""  # Ensure it’s not None

        if password1 != password2:
            raise forms.ValidationError("The two password fields must match.")

        if any(
            item.lower() in password1.lower()
            for item in [first_name, last_name, username]
            if item
        ):
            raise forms.ValidationError(
                "The password should not contain your first name, last name, or username."
            )

        return password2


class BecomeAProForm(forms.Form):
    business_name = forms.CharField(
        max_length=100,
        required=True,
        help_text="Required. Enter your business name or your name.",
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        help_text="Required. Enter your phone number.",
    )
    zip_code = forms.CharField(
        max_length=5,
        required=True,
        help_text="Required. Enter your zip code (Puerto Rico only).",
    )
    services = forms.MultipleChoiceField(
        choices=[],  # Choices will be set dynamically in the view
        required=True,
        widget=forms.SelectMultiple,
        help_text="Required. Select your service(s).",
    )

    def __init__(self, *args, **kwargs):
        services_choices = kwargs.pop("services_choices", [])
        super(BecomeAProForm, self).__init__(*args, **kwargs)
        self.fields["services"].choices = services_choices


class ProAccountForm(forms.ModelForm):
    class Meta:
        model = ProAccount
        fields = [
            "business_name",
            "phone_number",
            "zip_code",
            "languages",  # New field
            "business_email",  # New field
            "rates",
            "availability",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["services"] = list(
                self.instance.services.values_list("name", flat=True)
            )

    def clean_rates(self):
        rates = self.cleaned_data.get("rates")
        if rates:
            try:
                json.loads(rates)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for rates")
        return rates


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]
