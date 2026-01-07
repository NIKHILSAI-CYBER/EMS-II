from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings

from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, PasswordResetOTP
from .serializers import (
    UserSerializer,
    EmployeeProfileSerializer,
    ChangePasswordSerializer,
    CreateEmployeeSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    LoginTokenSerializer,
)
from .permissions import IsSuperAdmin
from .utils import generate_otp


# ================= AUTH =================
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if User.objects.filter(role="SUPER_ADMIN").exists():
            return Response({"error": "Super Admin already exists"}, status=400)

        User.objects.create_superuser(
            email=request.data["email"],
            password=request.data["password"],
            full_name=request.data["full_name"],
        )
        return Response({"message": "Super Admin created successfully"})


class LoginView(TokenObtainPairView):
    serializer_class = LoginTokenSerializer


# ================= ADMIN =================
class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        return Response({
            "total_employees": User.objects.filter(role="EMPLOYEE").count(),
            "active_users": User.objects.filter(is_active=True).count(),
        })


class AdminEmployeeListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        qs = User.objects.filter(role="EMPLOYEE")
        return Response(UserSerializer(qs, many=True).data)


class AdminCreateEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        serializer = CreateEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Employee created"})


class AdminEmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, employee_id):
        user = get_object_or_404(User, id=employee_id, role="EMPLOYEE")
        return Response({
            "user": UserSerializer(user).data,
            "profile": EmployeeProfileSerializer(user.profile).data,
        })


# ================= EMPLOYEE =================
class EmployeeProfileView(APIView):
    permission_classes = [IsAuthenticated]

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

        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response({"error": "Wrong password"}, status=400)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        return Response({"message": "Password updated"})


# ================= FORGOT PASSWORD =================
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(email=serializer.validated_data["email"]).first()
        if not user:
            return Response({"error": "Invalid email"}, status=400)

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
            return Response({"error": "Invalid email"}, status=400)

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=serializer.validated_data["otp"],
            is_used=False
        ).last()

        if not otp_obj or otp_obj.is_expired():
            return Response({"error": "Invalid or expired OTP"}, status=400)

        otp_obj.is_used = True
        otp_obj.save()

        return Response({"message": "OTP verified successfully"})


# ❌ NO OTP REQUIRED HERE
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(email=serializer.validated_data["email"]).first()
        if not user:
            return Response({"error": "Invalid email"}, status=400)

        otp_verified = PasswordResetOTP.objects.filter(
            user=user,
            is_used=True
        ).exists()

        if not otp_verified:
            return Response({"error": "OTP not verified"}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password reset successful"})
