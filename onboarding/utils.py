from django.core.mail import send_mail
from django.conf import settings
from .models import Onboarding

def send_onboarding_status_email(user, status, remarks=""):
    subject = f"Onboarding {status}"
    message = (
        f"Hello {user.full_name},\n\n"
        f"Your onboarding has been {status.lower()}.\n\n"
        f"Remarks: {remarks if remarks else 'N/A'}\n\n"
        f"Regards,\nEMS Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

# WRITE helper

def get_editable_onboarding(user):
    onboarding = Onboarding.objects.filter(employee=user).first()
    if not onboarding:
        return None, "Onboarding not found"

    if onboarding.status == "SUBMITTED":
        return None, "Onboarding already submitted"

    if onboarding.status == "APPROVED":
        return None, "Onboarding already approved"

    if onboarding.status == "REJECTED":
        # return None, "Onboarding rejected. Please wait for admin action."
        return onboarding, None

    if onboarding.status != "DRAFT":
        return None, "Onboarding is not editable"

    return onboarding, None


# def get_onboarding(user):
#     return Onboarding.objects.filter(employee=user).first()

# READ helper
def get_onboarding(user):
    onboarding = Onboarding.objects.filter(employee=user).first()
    if not onboarding:
        return None, "Onboarding not found"
    return onboarding, None

def ensure_section_editable(onboarding, section):
    if onboarding.status != "REJECTED":
        return True
    return onboarding.rejected_section == section