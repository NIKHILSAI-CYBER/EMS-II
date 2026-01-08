from rest_framework import serializers
from .models import (
    Onboarding, OnboardingDocument, OnboardingProfile, OnboardingEducation,
    OnboardingExperience, OnboardingIdentity, OnboardingBankDetails
)

class OnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Onboarding
        fields = (
            "id",
            "status",
            "submitted_at",
            "admin_remarks",
        )


class SubmitOnboardingSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()


class OnboardingDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingDocument
        fields = ("id", "document_type", "file", "is_verified", "uploaded_at")
        read_only_fields = ("is_verified", "uploaded_at")


class AdminOnboardingListSerializer(serializers.ModelSerializer):
    employee_email = serializers.CharField(source="employee.email", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = Onboarding
        fields = (
            "id",
            "employee_email",
            "employee_name",
            "status",
            "submitted_at",
        )


class AdminOnboardingDetailSerializer(serializers.ModelSerializer):
    employee_email = serializers.CharField(source="employee.email", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Onboarding
        fields = (
            "id",
            "employee_email",
            "employee_name",
            "status",
            "submitted_at",
            "admin_remarks",
            "documents",
        )

    def get_documents(self, obj):
        qs = obj.documents.all()
        return [
            {
                "id": d.id,
                "document_type": d.document_type,
                "file": d.file.url if d.file else None,
                "is_verified": d.is_verified,
                "uploaded_at": d.uploaded_at,
            }
            for d in qs
        ]


class ApproveRejectOnboardingSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["APPROVE", "REJECT"])
    admin_remarks = serializers.CharField(required=False, allow_blank=True)


class VerifyDocumentSerializer(serializers.Serializer):
    is_verified = serializers.BooleanField()


class OnboardingProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingProfile
        exclude = ("onboarding",)


class OnboardingEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingEducation
        exclude = ("onboarding",)


class OnboardingExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingExperience
        exclude = ("onboarding",)


class OnboardingIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingIdentity
        exclude = ("onboarding",)

    
class OnboardingBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingBankDetails
        exclude = ("onboarding",)