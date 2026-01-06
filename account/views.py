from django.shortcuts import render
# Create your views here.
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, LoginSerializer, ChangePasswordSerializer, CreateEmployeeSerializer, UpdateEmployeeSerializer
from .permissions import IsSuperAdmin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
# from .serializers import CustomTokenObtainPairSerializer


class DashboardView(APIView):
    def get(self, request):
        return Response({
            "total_employees": User.objects.filter(role="EMPLOYEE").count(),
            "active_users": User.objects.filter(is_active=True).count(),
        })
    
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if User.objects.filter(role="SUPER_ADMIN").exists():
            return Response(
                {"error": "Super Admin already exists"},
                status=400
            )

        user = User.objects.create_superuser(
            email=request.data["email"],
            password=request.data["password"],
            full_name=request.data["full_name"]
        )
        return Response({"message": "Super Admin created successfully"})

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
    
class EmployeeListView(APIView):
    def get(self, request):
        qs = User.objects.filter(role="EMPLOYEE")
        search = request.GET.get("search")

        if search:
            qs = qs.filter(full_name__icontains=search)

        return Response(UserSerializer(qs, many=True).data)
    
class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated]

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

class ProfileView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response({"error": "Wrong password"}, status=400)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.is_first_login = False
        request.user.save()

        return Response({"message": "Password updated"})
    
class CreateEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        serializer = CreateEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Employee created and email sent"})

class DeleteEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def delete(self, request, id):
        employee = User.objects.filter(
            id=id,
            role="EMPLOYEE"
        ).first()

        if not employee:
            return Response(
                {"error": "Employee not found"},
                status=404
            )

        employee.delete()
        return Response(
            {"message": "Employee deleted successfully"}
        )


class UpdateEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def put(self, request, id):
        employee = User.objects.filter(
            id=id,
            role="EMPLOYEE"
        ).first()

        if not employee:
            return Response(
                {"error": "Employee not found"},
                status=404
            )

        serializer = UpdateEmployeeSerializer(
            employee,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Employee updated successfully"}
        )
    
# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer



