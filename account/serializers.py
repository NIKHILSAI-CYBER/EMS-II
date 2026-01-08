from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from onboarding.models import Onboarding

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)


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
            # "email": user.email,
            # "full_name": user.full_name,
            # "is_first_login": user.is_first_login,
        }

class CreateEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "full_name", "department", "role")

    def create(self, validated_data):
        password = get_random_string(10)

        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            department=validated_data.get("department", ""),
            role=validated_data.get("role", "EMPLOYEE"),
            password=password,
        )

        # ✅ AUTO-CREATE ONBOARDING
        Onboarding.objects.create(
            employee=user
        )

        send_mail(
            subject="Your EMS Account Credentials",
            message=(
                f"Hello {user.full_name},\n\n"
                f"Your EMS account has been created.\n\n"
                f"Login Email: {user.email}\n"
                f"Temporary Password: {password}\n\n"
                f"Please log in and complete your onboarding."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user
    
# ✅ What This Guarantees

# Every employee always has onboarding

# No manual onboarding creation

# Clean 1-to-1 lifecycle


class UpdateEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("full_name", "department", "role", "is_active")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         token["role"] = user.role
#         token["email"] = user.email
#         token["full_name"] = user.full_name

#         return token