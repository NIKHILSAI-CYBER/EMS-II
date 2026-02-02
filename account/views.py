from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, AdminProfile
from onboarding.models import Onboarding
from .serializers import (UserSerializer, ChangePasswordSerializer, CreateEmployeeSerializer,
                          AdminUpdateEmployeeSerializer, ChangePasswordSerializer,
                          ForgotPasswordSerializer, VerifyOTPSerializer, EmployeeProfileSerializer,
                          LoginSerializer, ResetPasswordSerializer,   #UpdateEmployeeSerializer
                          AdminProfileSerializer

)
from onboarding.serializers import OnboardingProfileSerializer
from .permissions import IsSuperAdmin, IsPasswordChanged
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from .models import PasswordResetOTP
from .utils import generate_otp
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader
from rest_framework_simplejwt.tokens import RefreshToken


class AdminDashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        return Response({
            "employees": {
                "total": User.objects.filter(role="EMPLOYEE").count(),
                "active": User.objects.filter(role="EMPLOYEE", is_active=True).count(),
                "inactive": User.objects.filter(role="EMPLOYEE", is_active=False).count(),
            },
            "onboarding": {
                "draft": Onboarding.objects.filter(status="DRAFT").count(),
                "submitted": Onboarding.objects.filter(status="SUBMITTED").count(),
                "approved": Onboarding.objects.filter(status="APPROVED").count(),
                "rejected": Onboarding.objects.filter(status="REJECTED").count(),
                "pending_approvals": Onboarding.objects.filter(status="SUBMITTED").count(),
            }
        })

# class DashboardView(APIView):
#     def get(self, request):
#         return Response({
#             "total_employees": User.objects.filter(role="EMPLOYEE").count(),
#             "active_users": User.objects.filter(is_active=True).count(),
#         })
    

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )
    

# class LoginView(TokenObtainPairView):
#     serializer_class = LoginTokenSerializer
    
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if User.objects.filter(role="SUPER_ADMIN").exists():
            return Response({"error": "Super Admin already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        required_fields = ["email", "password", "full_name"]
        for field in required_fields:
            if not request.data.get(field):
                return Response(
                    {field: f"{field.replace('_', ' ').title()} is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        User.objects.create_superuser(
            email=request.data["email"],
            password=request.data["password"],
            full_name=request.data["full_name"],
        )
        return Response({"message": "Super Admin created successfully"}, status=status.HTTP_201_CREATED)



class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
    

class AdminEmployeeListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        qs = User.objects.filter(role="EMPLOYEE")
        return Response(UserSerializer(qs, many=True).data)

# class ProfileView(APIView):
#     def get(self, request):
#         return Response(UserSerializer(request.user).data)

#     def put(self, request):
#         serializer = UserSerializer(
#             request.user, data=request.data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
class EmployeeProfileView(APIView):
    permission_classes = [IsAuthenticated, IsPasswordChanged]

    def get(self, request):
        return Response({
            "user": UserSerializer(request.user).data,
            "profile": EmployeeProfileSerializer(request.user.profile).data,
        })

    def put(self, request):
        profile = request.user.profile

        serializer = EmployeeProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response({
            "message": "Profile updated successfully",
            "profile": serializer.data
        })
    
class EmployeeListView(APIView):
    def get(self, request):
        qs = User.objects.filter(role="EMPLOYEE")
        return Response(UserSerializer(qs, many=True).data)
    
class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated ] #IsEmployeeFullyOnboarded

    def get(self, request, id):
        employee = User.objects.filter(
            id=id,
            role="EMPLOYEE"
        ).first()

        if not employee:
            return Response(
                {"error": "Employee not found"},
                status=404
            )

        return Response({
            "id": employee.id,
            "email": employee.email,
            "full_name": employee.full_name,
            "department": employee.department,
            "role": employee.role,
            "is_active": employee.is_active
        })
    
# class CreateEmployeeView(APIView):
#     permission_classes = [IsSuperAdmin]

#     def post(self, request):
#         serializer = CreateEmployeeSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({"message": "Employee created"})

class AdminCreateEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        serializer = CreateEmployeeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(
            {"message": "Employee created successfully"},
            status=status.HTTP_201_CREATED
        )


class AdminEmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, employee_id):
        user = get_object_or_404(User, id=employee_id, role="EMPLOYEE")
        return Response({
            "user": UserSerializer(user).data,
            "profile": EmployeeProfileSerializer (user.profile).data,
        })
    def put(self, request, employee_id):
        user = get_object_or_404(User, id=employee_id, role="EMPLOYEE")

        serializer = AdminUpdateEmployeeSerializer(
            user,
            data=request.data,
            partial=True  # allow partial update
        )
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response({
            "message": "Employee updated successfully",
            "user": UserSerializer(user).data
        })
    
    def delete(self, request, employee_id):
        user = get_object_or_404(User, id=employee_id, role="EMPLOYEE")

        user.delete()

        return Response(
            {"message": "Employee deleted successfully"},
            status=status.HTTP_200_OK
        )


# ================= EMPLOYEE =================
# class EmployeeProfileView(APIView):
#     permission_classes = [IsAuthenticated, ] #IsPasswordChanged

#     def get(self, request):
#         return Response({
#             "user": UserSerializer(request.user).data,
#             "profile": (request.user.profile).data,
#         })
    
#     def put(self, request):
#         profile = request.user.profile

#         serializer = 
#             profile,
#             data=request.data,
#             partial=True  
        
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({
#             "message": "Profile updated successfully",
#             "profile": serializer.data
#         })

from onboarding.serializers import OnboardingProfileSerializer

class OnboardingProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        onboarding = request.user.onboarding

        return Response({
            "user": UserSerializer(request.user).data,
            "profile": OnboardingProfileSerializer(
                onboarding.profile
            ).data,
        })

    def put(self, request):
        onboarding = request.user.onboarding
        profile = onboarding.profile

        serializer = OnboardingProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Profile updated successfully",
            "profile": serializer.data
        })



class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data["new_password"])

        if user.is_first_login:
            user.is_first_login = False

        user.save()

        # return Response({"message": "Password updated successfully"})
        return Response({
            "message": "Password updated successfully",
            "is_first_login": user.is_first_login
        })


# class ChangePasswordView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = ChangePasswordSerializer(data=request.data)

#         if not serializer.is_valid():
#             return Response(
#                 {"errors": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         user = request.user

#         if not user.check_password(serializer.validated_data["old_password"]):
#             return Response(
#                 {"old_password": "Old password is incorrect"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         user.set_password(serializer.validated_data["new_password"])

#         if user.is_first_login:
#             user.is_first_login = False

#         user.save()

#         return Response({
#             "message": "Password updated successfully",
#             "is_first_login": user.is_first_login
#         })


# ================= FORGOT PASSWORD =================
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(email=serializer.validated_data["email"]).first()
        if not user:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
    

        otp = generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_mail(
            "EMS Password Reset OTP",
            f"Your OTP is {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        return Response({"message": "OTP sent"})
    

# ✅ OTP VERIFIED HERE ONLY
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(email=serializer.validated_data["email"]).first()
        if not user:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=serializer.validated_data["otp"],
            is_used=False
        ).last()

        if not otp_obj or otp_obj.is_expired():
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.is_used = True
        otp_obj.save()

        return Response({"message": "OTP verified successfully"})

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(
            email=serializer.validated_data["email"]
        ).first()

        if not user:
            return Response(
                {"email": "Email does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_verified = PasswordResetOTP.objects.filter(
            user=user,
            is_used=True
        ).exists()

        if not otp_verified:
            return Response(
                {"error": "OTP not verified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password reset successful"})


class AdminProfileDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]


    def get(self, request):
        profile, _ = AdminProfile.objects.get_or_create(
            user=request.user
        )

        serializer = AdminProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        profile, _ = AdminProfile.objects.get_or_create(user=request.user)

        image_file = request.FILES.get("image")
        data = request.data.copy()

        if image_file:
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="admin_profiles"
            )
            data["image"] = upload_result["secure_url"]

        serializer = AdminProfileSerializer(
            profile,
            data=data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response({
            "message": "Admin profile updated successfully",
            "profile": serializer.data
        })
    
# ❌ NO OTP REQUIRED HERE
# class ChangePasswordView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = ChangePasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         user = User.objects.filter(email=serializer.validated_data["email"]).first()
#         if not user:
#             return Response({"error": "Invalid email"}, status=400)

#         otp_verified = PasswordResetOTP.objects.filter(
#             user=user,
#             is_used=True
#         ).exists()

#         if not otp_verified:
#             return Response({"error": "OTP not verified"}, status=400)

#         user.set_password(serializer.validated_data["new_password"])
#         user.save()

#         return Response({"message": "Password reset successful"})



# class DeleteEmployeeView(APIView):
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def delete(self, request, id):
#         employee = User.objects.filter(
#             id=id,
#             role="EMPLOYEE"
#         ).first()

#         if not employee:
#             return Response(
#                 {"error": "Employee not found"},
#                 status=404
#             )

#         employee.delete()
#         return Response(
#             {"message": "Employee deleted successfully"}
#         )


# class UpdateEmployeeView(APIView):
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def put(self, request, id):
#         employee = User.objects.filter(
#             id=id,
#             role="EMPLOYEE"
#         ).first()

#         if not employee:
#             return Response(
#                 {"error": "Employee not found"},
#                 status=404
#             )

#         serializer = UpdateEmployeeSerializer(
#             employee,
#             data=request.data,
#             partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             {"message": "Employee updated successfully"}
#         )
    

# Employee is BLOCKED from:
# Dashboard, Employee list, Any business APIs
# Until:
# is_first_login = False AND onboarding.status = APPROVED


#APIs That MUST REMAIN OPEN
# /api/login/
# /api/change-password/
# /api/onboarding/my/
# /api/onboarding/submit/
# /api/onboarding/documents/upload/


    
# How Frontend Uses This
# Render admin dashboard cards
# Show “Pending Approvals” badge
# No extra API calls needed