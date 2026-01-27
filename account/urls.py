from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [


    # AUTH
    path("signup/", SignupView.as_view()),
    path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    # path("token/refresh/", TokenRefreshView.as_view()),
    # path("login/", CustomTokenObtainPairView.as_view()),


    #FORGOTPASSWORD
    path("forgot-password/", ForgotPasswordView.as_view()), 
    path("verify-otp/", VerifyOTPView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),

    #ADMIN
    path("admin/profile/",AdminProfileView.as_view()),
    path("admin/dashboard/metrics/", AdminDashboardMetricsView.as_view()), 
    # path("profile/", AdminProfileView.as_view()),
    path("admin/employees/create/",AdminCreateEmployeeView.as_view()),
    path("admin/employees/",AdminEmployeeListView.as_view()),
    path("admin/employees/<int:employee_id>/",AdminEmployeeDetailView.as_view()),
    path("admin/own/profile/",AdminProfileDetailView.as_view()),

    #EMPLOYEE
    # path("dashboard/", DashboardView.as_view()),
    path("employees/", EmployeeListView.as_view()),
    path("employees/<int:id>/",EmployeeDetailView.as_view()),
    path("employees/profile/",EmployeeProfileView.as_view()),
    path("employees/change-password/", ChangePasswordView.as_view()),
    # path("admin/employees/<int:id>/",DeleteEmployeeView.as_view()),
    # path("admin/employees/<int:id>/", EmployeeAdminView.as_view()),
    

]

    
    # # FORGOT PASSWORD
    # path("forgot-password/", ForgotPasswordView.as_view()),
    # path("verify-otp/", VerifyOTPView.as_view()),
    # path("reset-password/", ResetPasswordView.as_view()),

    # # ADMIN
    # path("admin/profile/", AdminProfileView.as_view()),
    # path("admin/dashboard/", AdminDashboardView.as_view()),
    # path("admin/employees/", AdminEmployeeListView.as_view()),
    # path("admin/employees/create/", AdminCreateEmployeeView.as_view()),
    # path("admin/employees/<int:employee_id>/", AdminEmployeeDetailView.as_view()),

    # # EMPLOYEE
    # path("employee/profile/", EmployeeProfileView.as_view()),
    # path("employee/change-password/", ChangePasswordView.as_view()),

# ]
# >>>>>>> origin/feature/account-updates
