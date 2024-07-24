from rest_framework import serializers


class CreateInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()


class OTPCheckSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    action = serializers.CharField(required=True)
