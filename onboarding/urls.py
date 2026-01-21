# from django.urls import path
# from .views import *


# urlpatterns = [
#     path("my/", MyOnboardingView.as_view()),
#     path("submit/", SubmitOnboardingView.as_view()),

#     path("documents/", OnboardingDocumentView.as_view()),
    
#     path("profiledata/", OnboardingProfileView.as_view()), 
#     path("education/", OnboardingEducationView.as_view()),  
#     path("experience/", OnboardingExperienceView.as_view()),
#     path("identity/", OnboardingIdentityView.as_view()),
#     path("bank/", OnboardingBankView.as_view()),

#     # path("documents/upload/", UploadOnboardingDocumentView.as_view()),
#     path("admin/submitted/", AdminOnboardingListView.as_view()),
#     path("admin/<int:id>/", AdminOnboardingDetailView.as_view()),
#     path("admin/<int:id>/action/", AdminOnboardingActionView.as_view()),
#     path("admin/documents/<int:id>/verify/",VerifyOnboardingDocumentView.as_view()),
    
#     path("onboarding/submit-status/", OnboardingSubmitStatusView.as_view(), name="onboarding-submit-status"),

# ]

from django.urls import path
from .views import *

urlpatterns = [
    path("my/", MyOnboardingView.as_view()),
    path("submit/", SubmitOnboardingView.as_view()),

    path("documents/", OnboardingDocumentView.as_view()),

    path("profiledata/", OnboardingProfileView.as_view()),
    path("education/", OnboardingEducationView.as_view()),
    path("experience/", OnboardingExperienceView.as_view()),
    path("identity/", OnboardingIdentityView.as_view()),
    path("bank/", OnboardingBankView.as_view()),

    path("admin/submitted/", AdminOnboardingListView.as_view()),
    path("admin/<int:id>/", AdminOnboardingDetailView.as_view()),
    path("admin/<int:id>/action/", AdminOnboardingActionView.as_view()),
    path("admin/documents/<int:id>/verify/", VerifyOnboardingDocumentView.as_view()),

    path("onboarding/submit-status/", OnboardingSubmitStatusView.as_view(), name="onboarding-submit-status"),
]
