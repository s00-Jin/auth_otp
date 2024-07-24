from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# Create your models here.
class OTP(models.Model):
    ACTION_CHOICES = [
        ("ResetPass", "Reset Password"),
        ("ChangePass", "Change Password"),
        ("Login", "Login"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    otp = models.CharField(max_length=6, unique=True)
    is_validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        now = timezone.now()
        return now < self.updated_at + timezone.timedelta(minutes=5)


class InviteOTP(models.Model):
    email = models.EmailField(unique=True)
    invite_otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
