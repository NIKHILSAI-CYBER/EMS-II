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
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = OnboardingDocument
        fields = (
            "id",
            "document_type",
            "file_url",
            "file_name",
            "is_verified",
            "uploaded_at",
        )

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split("/")[-1]
        return None

# class OnboardingDocumentSerializer(serializers.ModelSerializer):
#     file_url = serializers.SerializerMethodField()

#     class Meta:
#         model = OnboardingDocument
#         fields = ("id", "document_type", "file_url", "is_verified", "uploaded_at")

#     def get_file_url(self, obj):
#         return obj.file.url if obj.file else None
    

class OnboardingDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingDocument
        fields = ("document_type", "file")


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

    profile = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()
    bank = serializers.SerializerMethodField()

    educations = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    is_documents_verified = serializers.SerializerMethodField()

    class Meta:
        model = Onboarding
        fields = (
            "id",
            "employee_email",
            "employee_name",
            "status",
            "submitted_at",
            "admin_remarks",

            "is_documents_verified",

            "profile",
            "identity",
            "bank",

            "educations",
            "experiences",
            "documents",

            "employee",
            "reviewed_at",
        )


    def get_profile(self, obj):
        profile = getattr(obj, "profile", None)
        return OnboardingProfileSerializer(profile).data if profile else None

    def get_identity(self, obj):
        identity = getattr(obj, "identity", None)
        return OnboardingIdentitySerializer(identity).data if identity else None

    def get_bank(self, obj):
        bank = getattr(obj, "bank", None)
        return OnboardingBankSerializer(bank).data if bank else None

    def get_educations(self, obj):
        qs = obj.educations.all()
        return OnboardingEducationSerializer(qs, many=True).data

    def get_experiences(self, obj):
        qs = obj.experiences.all()
        return OnboardingExperienceSerializer(qs, many=True).data

    # def get_documents(self, obj):
    #     qs = obj.documents.all()
    #     return OnboardingDocumentSerializer(qs, many=True).data

    def get_documents(self, obj):
        qs = obj.documents.all()

        return OnboardingDocumentSerializer(
            qs,
            many=True,
            context=self.context
        ).data

    
    def get_is_documents_verified(self, obj):
        documents = obj.documents.all()

        if not documents.exists():
            return False

        return not documents.filter(is_verified=False).exists()
    
    # def get_is_documents_verified(self, obj):
    #     docs = obj.documents.all()
    #     if not docs.exists():
    #         return False
    #     return all(doc.is_verified for doc in docs)


# class ApproveRejectOnboardingSerializer(serializers.Serializer):
#     action = serializers.ChoiceField(choices=["APPROVE", "REJECT"])
#     admin_remarks = serializers.CharField(required=False)
#     rejected_section = serializers.ListField(
#         child=serializers.CharField(),
#         required=False
    # )


class ApproveRejectOnboardingSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["APPROVE", "REJECT"])
    admin_remarks = serializers.CharField(required=False)
    # rejected_sections = serializers.CharField(required=False)
    rejected_sections = serializers.ListField(
        child=serializers.CharField(),
        required=False
)


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