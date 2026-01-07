from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    # AUTH
    path("signup/", SignupView.as_view()), #Only Admin signup
    path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),

    # FORGOT PASSWORD
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),

    # ADMIN
    path("admin/profile/", AdminProfileView.as_view()),
    path("admin/dashboard/", AdminDashboardView.as_view()),
    path("admin/employees/", AdminEmployeeListView.as_view()),
    path("admin/employees/create/", AdminCreateEmployeeView.as_view()),
    path("admin/employees/<int:employee_id>/", AdminEmployeeDetailView.as_view()),

    # EMPLOYEE
    path("employee/profile/", EmployeeProfileView.as_view()),
    path("employee/change-password/", ChangePasswordView.as_view()),

]
