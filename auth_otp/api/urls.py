from django.urls import path

from .views.users import (
    LoginView,
    CustomTokenObtainPairView,
    SimpleGetView,
    RegisterCreateAPIView,
    ForgotPasswordOTPSent,
    ForgotPassword,
    ChangePasswordOTPSent,
    ChangePasswordAPIView,
    UserDeletionAPIView,
)
from .views.otp import InviteCreateAPIView, OTPCheckView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path(
        "login/otp-verify", CustomTokenObtainPairView.as_view(), name="login_otp_verify"
    ),
    path("register/", RegisterCreateAPIView.as_view(), name="register"),
    path(
        "forgot-password/OTP/",
        ForgotPasswordOTPSent.as_view(),
        name="forgot_password_otp",
    ),
    path("forgot-password/", ForgotPassword.as_view(), name="forgot_password"),
    path(
        "change-password/OTP/",
        ChangePasswordOTPSent.as_view(),
        name="change_password_otp",
    ),
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="change_password",
    ),
    path(
        "user-deletion/create/",
        UserDeletionAPIView.as_view(),
        name="user_deletion_record_creation",
    ),
    path("otp-check/", OTPCheckView.as_view(), name="otp_check"),
    path("invite-code/email/", InviteCreateAPIView.as_view(), name="invite-code_email"),
    path("simple-get/", SimpleGetView.as_view(), name="simple_get"),
]
