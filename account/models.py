from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("SUPER_ADMIN", "Super Admin"),
        ("EMPLOYEE", "Employee"),
    )

    DEPARTMENT_CHOICES = (
        ("developer", "Developer"),
        ("engineering", "Engineering"),
        ("marketing", "Marketing"),
        ("sales", "Sales"),
        ("human_resources", "Human Resources"),
        ("finance", "Finance"),
        ("operations", "Operations"),
        ("customer_support", "Customer Support"),
        ("product", "Product"),
    )

    STATUS_CHOICES = (
        (True, "Active"),
        (False, "Inactive"),
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    full_name = models.CharField(max_length=150)
    date_of_join = models.DateField(null=True, blank=True)
    company_name = models.CharField(max_length=150, blank=True)

    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        blank=True
    )

    designation = models.CharField(max_length=100, blank=True)
    reporting_manager = models.CharField(max_length=150, blank=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        db_index=True
    )

    is_active = models.BooleanField(
        default=True,
        choices=STATUS_CHOICES
    )

    is_staff = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"EMP-{get_random_string(6).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    dob = models.DateField(null=True, blank=True)
    father_name = models.CharField(max_length=150, blank=True)
    mother_name = models.CharField(max_length=150, blank=True)

    gender = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    nationality = models.CharField(max_length=50, blank=True)

    personal_email = models.EmailField(blank=True,null=True)
    contact_number = models.CharField(max_length=15, blank=True)
    alternate_phone_number = models.CharField(max_length=15, blank=True)

    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    address_line = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"

    def __str__(self):
        return f"Profile - {self.user.email}"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_otps"
    )

    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"

class AdminProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="admin_profile"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    # image = CloudinaryField("image", blank=True, null=True)
    image = models.URLField(blank=True, null=True)


    def _str_(self):
        return f"Admin Profile - {self.user.email}"