from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from account.permissions import IsPasswordChanged
from account.models import User
from .utils import get_onboarding, get_editable_onboarding

from .models import Onboarding, OnboardingDocument
from .serializers import (
    OnboardingSerializer,
    SubmitOnboardingSerializer,
    OnboardingDocumentSerializer,
    OnboardingDocumentUploadSerializer,
    AdminOnboardingListSerializer,
    AdminOnboardingDetailSerializer,
    ApproveRejectOnboardingSerializer,
    VerifyDocumentSerializer,
    OnboardingProfileSerializer, OnboardingEducationSerializer,
    OnboardingExperienceSerializer, OnboardingIdentitySerializer,
    OnboardingBankSerializer,
)

from onboarding.utils import get_editable_onboarding
from account.permissions import IsSuperAdmin
from onboarding.utils import send_onboarding_status_email
from .utils import get_onboarding

# GET my onboarding (employee)
class MyOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        onboarding = Onboarding.objects.filter(employee=request.user).first()
        if not onboarding:
            return Response({"error": "Onboarding not found"}, status=404)

        return Response(OnboardingSerializer(onboarding).data)


# SUBMIT onboarding (employee)
class SubmitOnboardingView(APIView):
    permission_classes = [IsAuthenticated]
  
    def post(self, request):
        onboarding = Onboarding.objects.filter(employee=request.user).first()
        if not onboarding:
            return Response({"error": "Onboarding not found"}, status=404)

        # ❗Prevent resubmission early
        if onboarding.status != "DRAFT":
            return Response(
                {"error": "Onboarding already submitted"},
                status=400
            )

        # ✅ Required validations
        if not hasattr(onboarding, "identity"):
            return Response({"error": "Identity details missing"}, status=400)

        if not onboarding.documents.exists():
            return Response({"error": "Documents not uploaded"}, status=400)

        # ✅ FINAL STATE CHANGE ONLY
        onboarding.status = "SUBMITTED"
        onboarding.submitted_at = timezone.now()
        onboarding.save(update_fields=["status", "submitted_at"])

        return Response({"message": "Onboarding submitted successfully"})

class OnboardingDocumentView(APIView):
    permission_classes = [IsAuthenticated, IsPasswordChanged]

    def get(self, request):
        onboarding, error = get_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        documents = onboarding.documents.all()
        return Response(
            OnboardingDocumentSerializer(documents, many=True).data,
            status=200
        )

    def post(self, request):
        onboarding, error = get_editable_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        serializer = OnboardingDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(onboarding=onboarding)

        return Response({"message": "Document uploaded"}, status=201)



# UPLOAD document (separate page)
# class UploadOnboardingDocumentView(APIView):


    # permission_classes = [IsAuthenticated]

    # def post(self, request):
    #     onboarding = Onboarding.objects.filter(employee=request.user).first()
    #     if not onboarding:
    #         return Response({"error": "Onboarding not found"}, status=404)

    #     serializer = OnboardingDocumentSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     serializer.save(onboarding=onboarding)
    #     return Response({"message": "Document uploaded"})

    # permission_classes = [IsAuthenticated, IsPasswordChanged]

    # def post(self, request):
    #     onboarding, error = get_editable_onboarding(request.user)
    #     if error:
    #         return Response({"error": error}, status=400)

    #     serializer = OnboardingDocumentUploadSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(onboarding=onboarding)

    #     return Response({"message": "Document uploaded"})


# LIST submitted onboardings (admin)
class AdminOnboardingListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        qs = Onboarding.objects.filter(status="SUBMITTED").order_by("-submitted_at")
        return Response(AdminOnboardingListSerializer(qs, many=True).data)


# VIEW onboarding details (admin)
class AdminOnboardingDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, id):
        onboarding = Onboarding.objects.filter(id=id).first()
        if not onboarding:
            return Response({"error": "Onboarding not found"}, status=404)

        return Response(AdminOnboardingDetailSerializer(onboarding).data)


# APPROVE / REJECT onboarding (admin)
# class AdminOnboardingActionView(APIView):
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def post(self, request, id):
#         onboarding = Onboarding.objects.filter(id=id).first()
#         if not onboarding:
#             return Response({"error": "Onboarding not found"}, status=404)

#         if onboarding.status != "SUBMITTED":
#             return Response(
#                 {"error": f"Cannot take action on {onboarding.status} onboarding"},
#                 status=400
#             )

#         serializer = ApproveRejectOnboardingSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         action = serializer.validated_data["action"]
#         remarks = serializer.validated_data.get("admin_remarks", "")

#         onboarding.admin_remarks = remarks
#         onboarding.reviewed_at = timezone.now()
#         onboarding.reviewed_by = request.user

#         if action == "APPROVE":
#             if onboarding.documents.filter(is_verified=False).exists():
#                 return Response(
#                     {"error": "All documents must be verified before approval"},
#                     status=400
#                 )
#             onboarding.status = "APPROVED"

#         else:  # REJECT
#             if not remarks:
#                 return Response(
#                     {"error": "Remarks are required when rejecting onboarding"},
#                     status=400
#                 )
#             onboarding.status = "REJECTED"

#         onboarding.save()

#         send_onboarding_status_email(
#             user=onboarding.employee,
#             status=onboarding.status,
#             remarks=remarks
#         )

#         return Response({
#             "message": f"Onboarding {onboarding.status.lower()} successfully"
#         })


class AdminOnboardingActionView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, id):
        onboarding = Onboarding.objects.filter(id=id, status="SUBMITTED").first()
        if not onboarding:
            return Response(
                {"error": "Onboarding not found or not in SUBMITTED state"},
                status=404
            )

        serializer = ApproveRejectOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        remarks = serializer.validated_data.get("admin_remarks", "")

        # 🔍 Document verification check (single source of truth)
        has_documents = onboarding.documents.exists()
        has_unverified_docs = onboarding.documents.filter(is_verified=False).exists()

        is_document_verified = has_documents and not has_unverified_docs

        onboarding.reviewed_at = timezone.now()
        onboarding.reviewed_by = request.user

        if action == "APPROVE":
            if not has_documents:
                return Response(
                    {"error": "No documents uploaded. Cannot approve onboarding."},
                    status=400
                )

            if not is_document_verified:
                return Response(
                    {
                        "error": "All documents must be verified before approval",
                        "is_document_verified": False
                    },
                    status=400
                )

            onboarding.status = "APPROVED"
            onboarding.admin_remarks = remarks

        elif action == "REJECT":
            if not remarks:
                return Response(
                    {"error": "admin_remarks is required when rejecting onboarding"},
                    status=400
                )

            onboarding.status = "REJECTED"
            onboarding.admin_remarks = remarks

        else:
            return Response(
                {"error": "Invalid action. Allowed values: APPROVE, REJECT"},
                status=400
            )

        onboarding.save()

        send_onboarding_status_email(
            user=onboarding.employee,
            status=onboarding.status,
            remarks=onboarding.admin_remarks
        )

        return Response({
            "message": f"Onboarding {onboarding.status.lower()} successfully",
            "status": onboarding.status,
            "is_document_verified": is_document_verified
        })



class VerifyOnboardingDocumentView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, id):
        document = OnboardingDocument.objects.filter(id=id).first()
        if not document:
            return Response({"error": "Document not found"}, status=404)

        serializer = VerifyDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document.is_verified = serializer.validated_data["is_verified"]
        document.save()

        return Response({
            "message": "Document verification updated",
            "document_id": document.id, 
            "is_verified": document.is_verified
        })


from account.permissions import IsPasswordChanged

class OnboardingProfileView(APIView):
    permission_classes = [IsAuthenticated, IsPasswordChanged]

    def post(self, request):
        onboarding, error = get_editable_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        obj = getattr(onboarding, "profile", None)
        serializer = (                                       #PUT/PATCH is NOT required - You are doing upsert-style POSTs:
            OnboardingProfileSerializer(obj, data=request.data, partial=True)
            if obj else OnboardingProfileSerializer(data=request.data)
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(onboarding=onboarding)
        return Response({"message": "Profile saved successfully"})

    def get(self, request):
        onboarding, error = get_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        profile = getattr(onboarding, "profile", None)
        if not profile:
            return Response({}, status=200)

        return Response(OnboardingProfileSerializer(profile).data)



class OnboardingEducationView(APIView):
    permission_classes = [IsAuthenticated, IsPasswordChanged]

    def post(self, request):
        onboarding, error = get_editable_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        serializer = OnboardingEducationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(onboarding=onboarding)
        return Response({"message": "Education added"})

    def get(self, request):
        onboarding, error = get_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        queryset = onboarding.educations.all()
        return Response(
            OnboardingEducationSerializer(queryset, many=True).data,
            status=200
        )
    

class OnboardingExperienceView(APIView):
    permission_classes = [IsAuthenticated, IsPasswordChanged]

    def post(self, request):
        onboarding, error = get_editable_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        serializer = OnboardingExperienceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(onboarding=onboarding)
        return Response({"message": "Experience added"})

    def get(self, request):
        onboarding, error = get_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        queryset = onboarding.experiences.all()
        return Response(
            OnboardingExperienceSerializer(queryset, many=True).data,
            status=200
        )

    
    
class OnboardingIdentityView(APIView):
    permission_classes = [IsAuthenticated, IsPasswordChanged]

    def post(self, request):
        onboarding, error = get_editable_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        obj = getattr(onboarding, "identity", None)
        serializer = (                                            #PUT/PATCH is NOT required - You are doing upsert-style POSTs:
            OnboardingIdentitySerializer(obj, data=request.data, partial=True)
            if obj else OnboardingIdentitySerializer(data=request.data)
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(onboarding=onboarding)
        return Response({"message": "Identity saved successfully"})
    def get(self, request):
        onboarding, error = get_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        identity = getattr(onboarding, "identity", None)
        documents = onboarding.documents.all()

        return Response({
            "identity": OnboardingIdentitySerializer(identity).data if identity else {},
            "documents": OnboardingDocumentSerializer(documents, many=True).data
        }, status=200)

    
class OnboardingBankView(APIView):
    permission_classes = [IsAuthenticated, IsPasswordChanged]

    def post(self, request):
        onboarding, error = get_editable_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        obj = getattr(onboarding, "bank", None)
        serializer = (                                #PUT/PATCH is NOT required - You are doing upsert-style POSTs:
            OnboardingBankSerializer(obj, data=request.data, partial=True)
            if obj else OnboardingBankSerializer(data=request.data)
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(onboarding=onboarding)
        return Response({"message": "Bank details saved"})

    def get(self, request):
        onboarding, error = get_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        obj = getattr(onboarding, "bank", None)
        return Response(
            OnboardingBankSerializer(obj).data if obj else {},
            status=200
        )


class MyOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        onboarding, error = get_onboarding(request.user)
        if error:
            return Response({"error": error}, status=400)

        return Response({
            "status": onboarding.status,
            "profile": (
                OnboardingProfileSerializer(onboarding.profile).data
                if hasattr(onboarding, "profile") else {}
            ),
            "identity": (
                OnboardingIdentitySerializer(onboarding.identity).data
                if hasattr(onboarding, "identity") else {}
            ),
            "bank": (
                OnboardingBankSerializer(onboarding.bank).data
                if hasattr(onboarding, "bank") else {}
            ),
            "educations": OnboardingEducationSerializer(
                onboarding.educations.all(), many=True
            ).data,
            "experiences": OnboardingExperienceSerializer(
                onboarding.experiences.all(), many=True
            ).data,
            "documents": OnboardingDocumentSerializer(
                onboarding.documents.all(), many=True
            ).data,
        })
    

class OnboardingSubmitStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        onboarding = Onboarding.objects.filter(employee=request.user).first()
        if not onboarding:
            return Response({"error": "Onboarding not found"}, status=404)

        # You can customize message based on status
        if onboarding.status == "SUBMITTED":
            msg = "Onboarding submitted successfully"
        elif onboarding.status == "APPROVED":
            msg = "Onboarding approved"
        elif onboarding.status == "REJECTED":
            msg = "Onboarding rejected"
        else:
            msg = "Onboarding in draft"

        return Response({
            "status": onboarding.status,
            "submitted_at": onboarding.submitted_at,
            "message": msg
        }, status=200)
    
# class GetOnboardingProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         onboarding = get_onboarding(request.user)
#         if not onboarding or not hasattr(onboarding, "profile"):
#             return Response({})
#         return Response(OnboardingProfileSerializer(onboarding.profile).data)

# class GetOnboardingEducationView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         onboarding = get_onboarding(request.user)
#         qs = onboarding.educations.all() if onboarding else []
#         return Response(OnboardingEducationSerializer(qs, many=True).data)

# class GetOnboardingExperienceView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         onboarding = get_onboarding(request.user)
#         qs = onboarding.experiences.all() if onboarding else []
#         return Response(OnboardingExperienceSerializer(qs, many=True).data)

# class GetOnboardingIdentityView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         onboarding = get_onboarding(request.user)
#         if not onboarding or not hasattr(onboarding, "identity"):
#             return Response({})
#         return Response(OnboardingIdentitySerializer(onboarding.identity).data)

# class GetOnboardingBankView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         onboarding = get_onboarding(request.user)
#         if not onboarding or not hasattr(onboarding, "bank"):
#             return Response({})
#         return Response(OnboardingBankSerializer(onboarding.bank).data)