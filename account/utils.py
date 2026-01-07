from django.utils.crypto import get_random_string
import random


# -----------------------------
# Generate random password
# -----------------------------
def generate_temp_password(length=10):
    return get_random_string(length)


# -----------------------------
# Generate 6-digit OTP
# -----------------------------
def generate_otp():
    return str(random.randint(100000, 999999))
