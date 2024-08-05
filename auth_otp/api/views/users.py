from django.contrib.auth import authenticate, get_user_model

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.users import (
    OTPLoginSerializer,
    CustomTokenObtainPairSerializer,
    RegisterCreateSerializer,
    ForgotChangePassSerializer,
    UserDeletionSerializer,
)
from ..serializers.otp import CreateInviteSerializer, OTPCheckSerializer
from ..services.otp import send_otp_email, check_otp
from auth_otp.otp.models import OTP
from auth_otp.users.models import ChangePasswordPreSave, UserDeletionPreSave


User = get_user_model()


class RegisterCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Successfully Registered."}, status=status.HTTP_201_CREATED
        )


class LoginView(generics.CreateAPIView):
    serializer_class = OTPLoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        action = "Login"

        authenticate_user = authenticate(email=email, password=password)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Email does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        if not authenticate_user:
            return Response(
                {"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
            )

        send_otp_email(user, action)

        return Response(
            {"message": "OTP(One Time Password) was sent to your email/mobile number"},
            status=status.HTTP_200_OK,
        )


class CustomTokenObtainPairView(generics.GenericAPIView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)


class ForgotPasswordOTPSent(generics.CreateAPIView):
    serializer_class = CreateInviteSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        action = "ResetPass"

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Email does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        send_otp_email(user, action)

        return Response(
            {"message": "OTP(One Time Password) was sent to your email/mobile number"},
            status=status.HTTP_200_OK,
        )


class ForgotPassword(generics.UpdateAPIView):
    serializer_class = ForgotChangePassSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        user_identifier = request.query_params.get("user_identifier")

        try:
            otp_instance = OTP.objects.get(user_identifier=user_identifier)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user = otp_instance.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user.set_password(serializer.validated_data["password"])
            user.save()
            otp_instance.delete()

            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordOTPSent(generics.CreateAPIView):
    serializer_class = ForgotChangePassSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        action = "ChangePass"

        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data.get("old_password")

            pre_save_pass = ChangePasswordPreSave.objects.create(user=user)

            if old_password and not user.check_password(old_password):
                return Response(
                    {"error": "Old password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            pre_save_pass.set_password(serializer.validated_data["password"])
            pre_save_pass.save()

            send_otp_email(user, action)
            return Response(
                {
                    "message": "OTP(One Time Password) was sent to your email/mobile number"
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(generics.UpdateAPIView):
    serializer_class = OTPCheckSerializer

    def update(self, request, *args, **kwargs):
        otp = request.data.get("otp")
        action = request.data.get("action")
        user_identifier = request.data.get("user_identifier")
        user = request.user

        otp_instance = check_otp(otp, action, user_identifier)

        if otp_instance.is_valid():
            otp_instance.is_validated = True
            try:
                change_password_instance = ChangePasswordPreSave.objects.get(
                    user=otp_instance.user
                )
            except ChangePasswordPreSave.DoesNotExist:
                return Response(
                    {"error": "Password change request not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.password = change_password_instance.password
            user.save()
            change_password_instance.delete()
            otp_instance.delete()
            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK,
            )
        otp_instance.delete()
        return Response(
            {"error": "Invalid OTP either expired OTP or wrong OTP"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserDeletionAPIView(generics.CreateAPIView):
    serializer_class = UserDeletionSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        reason = request.data.get("reason")
        action = request.data.get("action")

        send_otp_email(user, action)

        try:
            UserDeletionPreSave.objects.create(user=user, reason=reason)
            return Response(
                {"message": "User deletion request successfully made"},
                status=status.HTTP_201_CREATED,
            )
        except:
            return Response(
                {"Error": "User deletion request unsuccessful"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyUserDeletionAPIView(generics.CreateAPIView):
    serializer_class = OTPCheckSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        otp = request.data.get("otp")
        user_identifier = request.data.get("user_identifier")
        action = request.data.get("action")

        try:
            OTP.objects.get(otp=otp, user_identifier=user_identifier, action=action)
        except OTP.DoesNotExist:
            return Response(
                {"Error": "User deletion verification unsuccessful"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_delete = UserDeletionPreSave.objects.get(user=user)
        user_delete.is_verified = True
        user_delete.save()

        return Response(
            {"message": "User deletion request successfully verified"},
            status=status.HTTP_200_OK,
        )


class SimpleGetView(APIView):
    def get(self, request, *args, **kwargs):
        data = {"message": "Hello, this is a simple GET endpoint!"}
        return Response(data, status=status.HTTP_200_OK)
