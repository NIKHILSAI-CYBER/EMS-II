# from rest_framework import serializers
# <<<<<<< HEAD
# from django.contrib.auth import authenticate
# from .models import User
# =======
# >>>>>>> origin/feature/account-updates
# from django.utils.crypto import get_random_string
# from django.core.mail import send_mail
# from django.conf import settings
# <<<<<<< HEAD
# from rest_framework_simplejwt.tokens import RefreshToken
# from onboarding.models import Onboarding
# from .models import User, 

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, EmployeeProfile, AdminProfile
from onboarding.models import Onboarding
from django.db import transaction
from onboarding.models import OnboardingProfile

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         exclude = ("password",)
#         read_only_fields = ("email", "role")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)
        read_only_fields = (
            "employee_id",
            "email",
            "full_name",
            "date_of_join",
            "company_name",
            "department",
            "designation",
            "reporting_manager",
            "role",
            "is_active",
            )

class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = "__all__"
        read_only_fields = ("user",)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            email=attrs["email"],
            password=attrs["password"]
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid email or password"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled"
            )

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
            "email": user.email,
            "full_name": user.full_name,
            "is_first_login": user.is_first_login,
        }
    
    
# >>>>>>> origin/feature/account-updates
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         exclude = ("password",)
#         read_only_fields = (
#             "employee_id",
#             "email",
#             "full_name",
#             "date_of_join",
#             "company_name",
#             "department",
#             "designation",
#             "reporting_manager",
#             "role",
#         )


# <<<<<<< HEAD
# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         user = authenticate(
#             email=attrs["email"],
#             password=attrs["password"]
#         )

#         if not user:
#             raise serializers.ValidationError(
#                 "Invalid email or password"
#             )

#         if not user.is_active:
#             raise serializers.ValidationError(
#                 "User account is disabled"
#             )

#         refresh = RefreshToken.for_user(user)

#         return {
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#             "role": user.role,
#             # "email": user.email,
#             # "full_name": user.full_name,
#             # "is_first_login": user.is_first_login,
#         }


    
class CreateEmployeeSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            "email",
            "full_name",
            "date_of_join",
            "company_name",
            "department",
            "designation",
            "reporting_manager",
            "is_active",
        )


    def validate_email(self, value):
        return value.lower()


    def to_internal_value(self, data):
        # normalize is_active values
        if "is_active" in data:
            value = data.get("is_active")
            if isinstance(value, str):
                v = value.strip().lower()
                if v in ["false", "inactive", "0", "no"]:
                    data["is_active"] = False
                elif v in ["true", "active", "1", "yes"]:
                    data["is_active"] = True
        return super().to_internal_value(data)
    

    @transaction.atomic
    # def create(self, validated_data):
    #     password = get_random_string(10)
    #     is_active = validated_data.get("is_active", True)

    #     user = User.objects.create_user(
    #         email=validated_data["email"],
    #         full_name=validated_data["full_name"],
    #         date_of_join=validated_data.get("date_of_join"),
    #         company_name=validated_data.get("company_name", ""),
    #         department=validated_data.get("department", ""),
    #         designation=validated_data.get("designation", ""),
    #         reporting_manager=validated_data.get("reporting_manager", ""),
    #         role="EMPLOYEE",
    #         is_active=is_active,
    #         password=password,
    #     )

        # ✅ AUTO CREATE ONBOARDING (MANDATORY)
        # EmployeeProfile.objects.create(user=user)

    def create(self, validated_data):
        password = get_random_string(10)

        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            role="EMPLOYEE",
            password=password,
            is_active=True,
        )
        EmployeeProfile.objects.get_or_create(user=user)

        # ✅ ALWAYS ensure onboarding exists
        Onboarding.objects.get_or_create(employee=user)

        send_mail(
            subject="Your EMS Account Credentials",
            message=(
                f"Hello {user.full_name},\n\n"
                f"Login Email: {user.email}\n"
                f"Temporary Password: {password}\n\n"
                f"Please log in and complete your onboarding."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return user





# class CreateEmployeeSerializer(serializers.ModelSerializer):
#     is_active = serializers.BooleanField(required=False)

#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "full_name",
#             "date_of_join",
#             "company_name",
#             "department",
#             "designation",
#             "reporting_manager",
#             "is_active",
#         )

#     def validate_email(self, value):
#         return value.lower()

#     def create(self, validated_data):
#         password = get_random_string(10)

#         is_active = validated_data.pop("is_active", True)

#         user = User.objects.create_user(
#             email=validated_data["email"],
#             full_name=validated_data["full_name"],
#             date_of_join=validated_data.get("date_of_join"),
#             company_name=validated_data.get("company_name", ""),
#             department=validated_data.get("department", ""),
#             designation=validated_data.get("designation", ""),
#             reporting_manager=validated_data.get("reporting_manager", ""),
#             role="EMPLOYEE",
#             is_active=is_active,
#             password=password,
#         )

#         EmployeeProfile.objects.create(user=user)

#         send_mail(
#             subject="Your EMS Account Credentials",
#             message=(
#                 f"Hello {user.full_name},\n\n"
#                 f"Login Email: {user.email}\n"
#                 f"Temporary Password: {password}"
#             ),
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#         )

#         return user
# >>>>>>> origin/feature/account-updates
# class CreateEmployeeSerializer(serializers.ModelSerializer):
#     is_active = serializers.BooleanField(required=False)

#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "full_name",
#             "date_of_join",
#             "company_name",
#             "department",
#             "designation",
#             "reporting_manager",
#             "is_active",
#         )

#     def validate_email(self, value):
#         return value.lower()

#     def to_internal_value(self, data):
#         """
#         🔥 CRITICAL FIX
#         Normalizes is_active from frontend
#         """
#         if "is_active" in data:
#             value = data.get("is_active")

#             if isinstance(value, str):
#                 v = value.strip().lower()
#                 if v in ["false", "inactive", "0", "no"]:
#                     data["is_active"] = False
#                 elif v in ["true", "active", "1", "yes"]:
#                     data["is_active"] = True

#         return super().to_internal_value(data)

#     def create(self, validated_data):
#         password = get_random_string(10)

#         is_active = validated_data.get("is_active", True)

#         user = User.objects.create_user(
#             email=validated_data["email"],
#             full_name=validated_data["full_name"],
#             date_of_join=validated_data.get("date_of_join"),
#             company_name=validated_data.get("company_name", ""),
#             department=validated_data.get("department", ""),
#             designation=validated_data.get("designation", ""),
#             reporting_manager=validated_data.get("reporting_manager", ""),
#             role="EMPLOYEE",
#             is_active=is_active,
#             password=password,
#         )

# <<<<<<< HEAD
#         # ✅ AUTO-CREATE ONBOARDING
#         Onboarding.objects.create(
#             employee=user
#         )
# =======
#         # EmployeeProfile.objects.create(user=user)
# >>>>>>> origin/feature/account-updates

#         send_mail(
#             subject="Your EMS Account Credentials",
#             message=(
#                 f"Hello {user.full_name},\n\n"
#                 f"Login Email: {user.email}\n"
# <<<<<<< HEAD
#                 f"Temporary Password: {password}\n\n"
#                 f"Please log in and complete your onboarding."
# =======
#                 f"Temporary Password: {password}"
# >>>>>>> origin/feature/account-updates
#             ),
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#         )

#         return user


# ✅ What This Guarantees

# Every employee always has onboarding

# No manual onboarding creation

# Clean 1-to-1 lifecycle


# class UpdateEmployeeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("full_name", "department", "role", "is_active")


class AdminUpdateEmployeeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            "email",
            "full_name",
            "role",
            "date_of_join",
            "company_name",
            "department",
            "designation",
            "reporting_manager",
            "is_active",
        )

    def validate_email(self, value):
        return value.lower()

    def to_internal_value(self, data):
        """
        Normalize is_active values (same logic as create)
        """
        if "is_active" in data:
            value = data.get("is_active")

            if isinstance(value, str):
                v = value.strip().lower()
                if v in ["false", "inactive", "0", "no"]:
                    data["is_active"] = False
                elif v in ["true", "active", "1", "yes"]:
                    data["is_active"] = True

        return super().to_internal_value(data)
    

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True,
                                         error_messages={"required": "Old password is required"})
    new_password = serializers.CharField(write_only=True,
                                         error_messages={"required": "New password is required"})
    confirm_password = serializers.CharField(write_only=True,
                                        error_messages={"required": "Confirm password is required"})

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New password and confirm password do not match"}
            )
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "required": "Email is required",
            "blank": "Email cannot be empty",
            "invalid": "Enter a valid email address",
        }

    )


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "required": "Email is required",
            "invalid": "Enter a valid email address",
        }

    )

    otp = serializers.CharField(max_length=6,
        error_messages={
            "required": "OTP is required",
            "blank": "OTP cannot be empty",
        }
                                )


class LoginTokenSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email:
            raise serializers.ValidationError({"email": "Email is required"})

        if not password:
            raise serializers.ValidationError({"password": "Password is required"})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Email does not exist"})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password"})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Your account is inactive"})

        data = super().validate(attrs)

        data["role"] = user.role
        data["is_first_login"] = user.is_first_login

        return data


class AdminProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    # image = serializers.ImageField(required=False, allow_null=True)
    image = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = AdminProfile
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "image",
        )



