from rest_framework import serializers
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, EmployeeProfile


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
        )


class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = "__all__"
        read_only_fields = ("user",)


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
        """
        🔥 CRITICAL FIX
        Normalizes is_active from frontend
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

    def create(self, validated_data):
        password = get_random_string(10)

        is_active = validated_data.get("is_active", True)

        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            date_of_join=validated_data.get("date_of_join"),
            company_name=validated_data.get("company_name", ""),
            department=validated_data.get("department", ""),
            designation=validated_data.get("designation", ""),
            reporting_manager=validated_data.get("reporting_manager", ""),
            role="EMPLOYEE",
            is_active=is_active,
            password=password,
        )

        EmployeeProfile.objects.create(user=user)

        send_mail(
            subject="Your EMS Account Credentials",
            message=(
                f"Hello {user.full_name},\n\n"
                f"Login Email: {user.email}\n"
                f"Temporary Password: {password}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return user



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


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New password and confirm password do not match"}
            )
        return data



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data


class LoginTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data["role"] = self.user.role
        data["is_first_login"] = self.user.is_first_login  # ✅ ADD

        return data

