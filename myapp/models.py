from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class MyUserManager(BaseUserManager):
    def create_user(
        self, username, email, first_name, last_name, password=None
    ):
        if not username:
            raise ValueError("Users must have a username")
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        UserProfile.objects.create(
            user=user
        )  # Create a UserProfile for the new user
        return user

    def create_superuser(
        self, username, email, first_name, last_name, password
    ):
        user = self.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_superuser = True  # Only set is_superuser
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30, default="")
    last_name = models.CharField(max_length=30, default="")
    is_active = models.BooleanField(default=True)
    is_pro = models.BooleanField(default=False)
    pro_account_created_at = models.DateTimeField(null=True, blank=True)
    objects = MyUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser  # Changed from is_admin to is_superuser
    
    @is_staff.setter
    def is_staff(self, value):
        """Allow setting the is_staff property."""
        self.is_superuser = value

class UserProfile(models.Model):
    user = models.OneToOneField(
        MyUser, on_delete=models.CASCADE, related_name="profile"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        db_table = "myapp_userprofile"


class PasswordResetCode(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset code for {self.user.email}"


class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProAccount(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    services = models.ManyToManyField(Service)
    rates = models.TextField(blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)
    become_a_pro_completed = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    languages = models.TextField(blank=True, null=True)
    profile_visibility = models.BooleanField(default=True)
    business_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Pro Account"


class ZipCode(models.Model):
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "myapp_zipcodes"
