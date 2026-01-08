from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Onboarding(models.Model):
    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    employee = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="onboarding"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_onboardings"
    )

    admin_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.status}"
    


class OnboardingDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = (
        ("AADHAR", "Aadhar"),
        ("PAN", "PAN"),
        ("RESUME", "Resume"),
        ("PHOTO", "Photo"),
        ("OTHER", "Other"),
    )

    onboarding = models.ForeignKey(
        Onboarding,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES
    )

    file = models.FileField(upload_to="onboarding_documents/")
    is_verified = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} - {self.onboarding.employee}"
    


# OneToOne onboarding per employee (matches reality)

# Draft → Submitted → Approved/Rejected lifecycle

# Separate document table (scalable)

# Admin review metadata supported


class OnboardingProfile(models.Model):
    onboarding = models.OneToOneField(Onboarding, on_delete=models.CASCADE, related_name="profile")

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=150)

    gender = models.CharField(max_length=20)
    dob = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20)

    personal_email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    alternate_number = models.CharField(max_length=15, blank=True)

    nationality = models.CharField(max_length=50)
    physically_handicapped = models.BooleanField(default=False)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)



class OnboardingEducation(models.Model):
    onboarding = models.ForeignKey(Onboarding, on_delete=models.CASCADE, related_name="educations")

    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=150)
    institution_name = models.CharField(max_length=150)
    year_of_passing = models.IntegerField()
    grade_percentage = models.CharField(max_length=20)
    education_type = models.CharField(max_length=50)  # Full-time / Part-time



class OnboardingExperience(models.Model):
    onboarding = models.ForeignKey(Onboarding, on_delete=models.CASCADE, related_name="experiences")

    previous_company = models.CharField(max_length=150)
    designation = models.CharField(max_length=100)
    experience_from = models.DateField()
    experience_to = models.DateField()
    description = models.TextField(blank=True)


class OnboardingIdentity(models.Model):
    onboarding = models.OneToOneField(Onboarding, on_delete=models.CASCADE, related_name="identity")

    aadhaar_number = models.CharField(max_length=12, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    voter_id = models.CharField(max_length=20, blank=True)
    uan_number = models.CharField(max_length=20, blank=True)



class OnboardingBankDetails(models.Model):
    onboarding = models.OneToOneField(Onboarding, on_delete=models.CASCADE, related_name="bank")

    account_holder_name = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=150)
    account_type = models.CharField(max_length=50)