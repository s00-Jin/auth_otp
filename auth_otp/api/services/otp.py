import pyotp

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError


from auth_otp.otp.models import OTP, InviteOTP


User = get_user_model()


def send_otp_email(user, action):
    totp_6 = pyotp.TOTP(pyotp.random_base32(), interval=300)
    totp_4 = pyotp.TOTP(pyotp.random_base32(), digits=4, interval=300)
    otp_4 = totp_4.now()
    otp_6 = totp_6.now()

    otpmodel, created = OTP.objects.get_or_create(user=user, action=action)

    otpmodel.otp = otp_6
    otpmodel.user_identifier = otp_4
    otpmodel.action = action
    otpmodel.save()

    subject = f"Your OTP for {action}"
    html_content = render_to_string(
        "otp_email.html", {"otp_6": otp_6, "otp_4": otp_4, "username": user.username}
    )
    text_content = strip_tags(html_content)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    # Send email using Django's send_mail function
    send_mail(
        subject,
        text_content,
        from_email,
        recipient_list,
        html_message=html_content,
    )


def send_invite_email(email, action):
    totp_6 = pyotp.TOTP(pyotp.random_base32(), interval=300)
    otp_6 = totp_6.now()

    InviteOTP.objects.create(email=email, invite_otp=otp_6)

    subject = "You're Invited! Join [App Name] with Your Invitation Code"
    html_content = render_to_string(
        "invite_email.html", {"otp_6": otp_6, "username": email}
    )
    text_content = strip_tags(html_content)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    # Send email using Django's send_mail function
    send_mail(
        subject,
        text_content,
        from_email,
        recipient_list,
        html_message=html_content,
    )


def check_otp(otp, action, user_identifier):

    try:
        otp_instance = OTP.objects.get(
            otp=otp, action=action, user_identifier=user_identifier
        )
    except OTP.DoesNotExist:
        raise ValidationError({"error": "Invalid OTP"})
    return otp_instance
