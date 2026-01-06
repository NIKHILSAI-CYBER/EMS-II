from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    
    path("signup/", SignupView.as_view()),
    path("login/", LoginView.as_view()),
    # path("token/refresh/", TokenRefreshView.as_view()),
    # path("login/", CustomTokenObtainPairView.as_view()),/

    path("token/refresh/", TokenRefreshView.as_view()),

    path("dashboard/", DashboardView.as_view()),
    path("employees/", EmployeeListView.as_view()),
    path("employees/<int:id>/",EmployeeDetailView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),

    path("admin/create-employee/", CreateEmployeeView.as_view()),
    path("admin/employees/<int:id>/",DeleteEmployeeView.as_view()),
    path("admin/employees/<int:id>/",UpdateEmployeeView.as_view()),
    # path("admin/employees/<int:id>/", EmployeeAdminView.as_view()),
    
    

]