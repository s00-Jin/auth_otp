from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from auth_otp.otp.models import InviteOTP
from auth_otp.users.models import User

from ..services.otp import check_otp

from django.contrib.auth.models import update_last_login
from django.conf import settings


class RegisterCreateSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    invite_code = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "re_password",
            "first_name",
            "last_name",
            "middle_name",
            "contact_number",
            "address",
            "invite_code",
        ]

    def validate(self, data):
        if data["password"] != data["re_password"]:
            raise serializers.ValidationError(
                {"error": "password and re_password fields didn't match"}
            )
        return data

    def create(self, validated_data):
        invite_code = validated_data.pop("invite_code", None)
        validated_data.pop("re_password")
        email = validated_data["email"]

        if settings.INVITE_STATUS:
            try:
                instance = InviteOTP.objects.get(invite_otp=invite_code, email=email)
            except InviteOTP.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "invite_code": "Invalid invite code or email(Note: Used the invited email address in registering to the app/website)."
                    }
                )

            if instance.is_used:
                raise serializers.ValidationError(
                    {
                        "invite_code": "Email is already registered, Invite code already used"
                    }
                )

            instance.is_used = True
            instance.save()

        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    user_identifier = serializers.CharField(required=True)
    action = serializers.CharField(required=True)

    def validate(self, attrs):
        otp = attrs.get("otp")
        action = attrs.get("action")
        user_identifier = attrs.get("user_identifier")
        user = None

        otp_instance = check_otp(otp, action, user_identifier)

        if otp_instance.is_valid():
            otp_instance.delete()
            user = User.objects.get(email=otp_instance.user)
            refresh = self.get_token(user)

            data = {}
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, user)

            return data
        otp_instance.delete()
        raise ValidationError({"error": "OTP is expired"})

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)


class OTPLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ForgotChangePassSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    re_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        password = attrs.get("password")
        re_password = attrs.get("re_password")

        if password != re_password:
            raise serializers.ValidationError(
                {"error": "password and re_password fields didn't match"}
            )
        return attrs
