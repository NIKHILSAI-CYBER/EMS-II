from rest_framework import serializers
from .models import User
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)


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

        # Email credentials
        send_mail(
            subject="Your EMS Account Credentials",
            message=(
                f"Hello {user.full_name},\n\n"
                f"Your EMS account has been created.\n\n"
                f"Login Email: {user.email}\n"
                f"Temporary Password: {password}\n\n"
                f"Please log in and change your password immediately."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()