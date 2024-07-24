from django.contrib.auth import authenticate, get_user_model


from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers.users import (
    OTPLoginSerializer,
    CustomTokenObtainPairSerializer,
    RegisterCreateSerializer,
    ForgotChangePassSerializer,
)
from ..serializers.otp import CreateInviteSerializer
from ..services.otp import send_otp_email
from rest_framework.views import APIView


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


class SimpleGetView(APIView):
    def get(self, request, *args, **kwargs):
        data = {"message": "Hello, this is a simple GET endpoint!"}
        return Response(data, status=status.HTTP_200_OK)
