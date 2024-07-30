from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


from ..permissions import IsAuthenticatedAndStaff
from ..serializers.otp import CreateInviteSerializer, OTPCheckSerializer
from ..services.otp import send_invite_email, check_otp

from auth_otp.users.models import ChangePasswordPreSave

from django.contrib.auth import get_user_model

User = get_user_model()


class InviteCreateAPIView(generics.CreateAPIView):
    serializer_class = CreateInviteSerializer
    permission_classes = [IsAuthenticatedAndStaff]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        action = "Invite code"

        send_invite_email(email, action)

        return Response(
            {
                "message": "Invite code was sent to the email/mobile number you have entered"
            },
            status=status.HTTP_200_OK,
        )


class OTPCheckView(generics.CreateAPIView):
    serializer_class = OTPCheckSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        otp = request.data.get("otp")
        action = request.data.get("action")
        user_identifier = request.data.get("user_identifier")

        otp_instance = check_otp(otp, action, user_identifier)
        user = User.objects.get(email=otp_instance.user)

        if otp_instance.is_valid():
            otp_instance.is_validated = True
            if otp_instance.action == "ResetPass":
                return Response(
                    {
                        "message": {
                            "status": "OTP Validated",
                            "Forgot-pass-url": f"http://localhost/api/forgot-password/?user_identifier={otp_instance.user_identifier}",
                        }
                    },
                    status=status.HTTP_200_OK,
                )
        otp_instance.delete()
        return Response(
            {"error": "Invalid OTP either expired OTP or wrong OTP"},
            status=status.HTTP_400_BAD_REQUEST,
        )
