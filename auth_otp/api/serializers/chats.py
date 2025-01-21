from rest_framework import serializers
from rest_framework.response import Response

from auth_otp.chats.models import Chat, Participant, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=True
    )

    class Meta:
        model = Chat
        fields = ["id", "name", "created_at", "updated_at", "participants"]

    def validate(self, data):
        participants = data.get("participants", [])
        request = self.context.get("request")

        # Include the request user in participants
        if request and request.user.username not in participants:
            participants.append(request.user.username)

        participant_instances = User.objects.filter(username__in=participants)

        if len(participants) == 2:
            participant_usernames = sorted([p.username for p in participant_instances])
            existing_chat = Chat.objects.filter(
                is_group_chat=False,
                name__in=[
                    f"{participant_usernames[0]} + {participant_usernames[1]}",
                    f"{participant_usernames[1]} + {participant_usernames[0]}",
                ],
            ).first()

            if existing_chat:
                return Response({"existing_chat": existing_chat.id})

        return data

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        request = self.context.get("request")

        # Include the request user in participants
        participants.append(request.user.username)

        # Check if there is an existing chat with the same participants
        participant_instances = User.objects.filter(username__in=participants)

        participant_usernames = sorted([p.username for p in participant_instances])
        chat = super().create(validated_data)
        chat.is_group_chat = False
        chat.name = f"{participant_usernames[0]} + {participant_usernames[1]}"

        chat = super().create(validated_data)
        chat.name = f"chatroom_{chat.id}"

        chat.save()

        for participant in participant_instances:
            Participant.objects.create(chat=chat, user=participant)

        return chat


class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Participant
        fields = [
            "id",
            "user",
            "nickname",
            "joined_at",
            "chat",
            "is_approved",
            "is_admin",
        ]


class MessageSerializer(serializers.ModelSerializer):
    sender = ParticipantSerializer(read_only=True)
    content = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "content", "timestamp", "is_read"]

    def get_content(self, obj):
        return obj.get_decrypted_content()
