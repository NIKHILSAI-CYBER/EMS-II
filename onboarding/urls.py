from django.urls import path
from .views import *


urlpatterns = [
    path("my/", MyOnboardingView.as_view()),
    path("submit/", SubmitOnboardingView.as_view()),
    path("documents/upload/", UploadOnboardingDocumentView.as_view()),
    path("admin/submitted/", AdminOnboardingListView.as_view()),
    path("admin/<int:id>/", AdminOnboardingDetailView.as_view()),
    path("admin/<int:id>/action/", AdminOnboardingActionView.as_view()),
    path("admin/documents/<int:id>/verify/",VerifyOnboardingDocumentView.as_view()),
    path("profile/", OnboardingProfileView.as_view()),
    path("education/", OnboardingEducationView.as_view()),
    path("experience/", OnboardingExperienceView.as_view()),
    path("identity/", OnboardingIdentityView.as_view()),
    path("bank/", OnboardingBankView.as_view()),
    path("get/profile/", GetOnboardingProfileView.as_view()),
    path("get/education/", GetOnboardingEducationView.as_view()),
    path("get/experience/", GetOnboardingExperienceView.as_view()),
    path("get/identity/", GetOnboardingIdentityView.as_view()),
    path("get/bank/", GetOnboardingBankView.as_view()),
]