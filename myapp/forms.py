from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = UserModel
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, help_text='Enter the 6-digit code sent to your email.')
