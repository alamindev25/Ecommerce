from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import random
import os
import requests
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(
        self, phone, password=None, role="user", is_active=True, **extra_fields
    ):
        if not phone:
            raise ValueError("User must have a phone number.")
        if not password:
            raise ValueError("User must have a password.")

        user_obj = self.model(
            phone=phone, role=role, is_active=is_active, **extra_fields
        )
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone, password=None):
        return self.create_user(phone, password=password, is_staff=True)

    def create_agent(self, phone, password=None):
        return self.create_user(phone, password=password, role="agent")

    def create_custom_admin(self, phone, password=None):
        return self.create_user(phone, password=password, role="custom_admin")

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    BUSINESS_CHOICES = [
        ("POULTRY", "Poultry"),
        ("GROCERY", "Grocery"),
    ]

    ROLE_CHOICES = (
        ("user", "User"),
        ("agent", "Agent"),
        ("staff", "Staff"),
        ("admin", "Admin"),
        ("custom_admin", "Custom_admin")
    )

    phone_regex = RegexValidator(
        r"^\d{10}$", message="Phone number must be 10 digits only."
    )
    phone = models.CharField(validators=[phone_regex], max_length=10, unique=True)
    business_type = models.CharField(
        max_length=10,
        choices=BUSINESS_CHOICES,
        default="POULTRY",
        blank=False,
        null=False,
        help_text="Select either Poultry or Grocery",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    first_login = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        if self.is_admin and self.is_active:
            return True
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return self.is_admin

    def __str__(self):
        return self.phone

    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    @property
    def is_agent(self):
        return self.role == "agent"

    @property
    def is_custom_user(self):
        return self.role == "custom_admin"


class PhoneOTP(models.Model):
    phone_regex = RegexValidator(
        r"^\d{10}$", message="Phone number must be entered in the form."
    )
    phone = models.CharField(validators=[phone_regex], max_length=10, unique=True)
    otp = models.CharField(max_length=10, blank=True, null=True)
    count = models.IntegerField(default=0, help_text="Number of otp sent")
    validated = models.BooleanField(
        default=False,
        help_text="If it is true, that means user has validated otp correctly in second API",
    )

    def __str__(self):
        return f"{self.phone} is sent {self.otp}"
