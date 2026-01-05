from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    
    path("signup/", SignupView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),

    path("dashboard/", DashboardView.as_view()),
    path("employees/", EmployeeListView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),

    path("admin/create-employee/", CreateEmployeeView.as_view()),
]