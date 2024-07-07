from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = UserModel
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserModel.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different one.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists. Please use a different email address.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        username = self.cleaned_data.get('username')
        
        if password1 != password2:
            raise forms.ValidationError('The two password fields must match.')
        
        if any(item in password1.lower() for item in [first_name.lower(), last_name.lower(), username.lower()]):
            raise forms.ValidationError('The password should not contain your first name, last name, or username.')
        
        return password2

class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, help_text='Enter the 6-digit code sent to your email.')

class CustomSetPasswordForm(SetPasswordForm):
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        first_name = self.user.first_name
        last_name = self.user.last_name
        username = self.user.username

        if password1 != password2:
            raise forms.ValidationError('The two password fields must match.')

        if any(item in password1.lower() for item in [first_name.lower(), last_name.lower(), username.lower()]):
            raise forms.ValidationError('The password should not contain your first name, last name, or username.')

        return password2
