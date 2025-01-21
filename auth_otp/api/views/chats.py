from rest_framework import generics, status, permissions
from rest_framework.response import Response
from auth_otp.chats.models import Chat, Participant, Message
from ..serializers.chats import ChatSerializer, ParticipantSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatCreateView(generics.CreateAPIView):

    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        chat = serializer.save()
        Participant.objects.create(chat=chat, user=self.request.user, is_admin=True)


class ChatListView(generics.ListAPIView):

    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(participants__user=self.request.user)


class ParticipantListView(generics.ListAPIView):

    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return Participant.objects.filter(chat_id=chat_id)


class MessageListView(generics.ListAPIView):

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return Message.objects.filter(chat_id=chat_id).order_by("timestamp")


class UserChatsView(generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        chats = Chat.objects.filter(participants__user=user)

        user_chats = []

        for chat in chats:
            if chat.is_group_chat:
                chat_name = chat.name or f"Group Chat {chat.id}"
            else:
                other_participant = chat.participants.exclude(user=user).first()
                chat_name = (
                    other_participant.nickname or other_participant.user.username
                )

            user_chats.append(
                {
                    "chat_id": chat.id,
                    "chat_name": chat_name,
                }
            )

        return Response(user_chats, status=status.HTTP_200_OK)


class AddParticipantView(generics.CreateAPIView):

    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs["chat_id"]
        chat = Chat.objects.get(id=chat_id)
        user_to_add = User.objects.get(id=request.data["user_id"])
        participant, created = Participant.objects.get_or_create(
            chat=chat, user=user_to_add
        )

        if created:
            # If the participant is added, set is_approved to False initially
            participant.is_approved = False
            participant.save()
            return Response(
                {"status": "Participant added, waiting for admin approval"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": "Participant already in the chat"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PendingApprovalListView(generics.ListAPIView):

    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return Participant.objects.filter(chat_id=chat_id, is_approved=False)


class ApproveParticipantView(generics.UpdateAPIView):

    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs["chat_id"]
        participant_id = request.data["user_id"]
        chat = Chat.objects.get(id=chat_id)
        participant = Participant.objects.get(chat=chat, user_id=participant_id)

        if request.user not in chat.participants.filter(is_admin=True):
            return Response(
                {"status": "Only admins can approve participants"},
                status=status.HTTP_403_FORBIDDEN,
            )

        participant.is_approved = True
        participant.save()
        return Response({"status": "Participant approved"}, status=status.HTTP_200_OK)


class AddAdminView(generics.UpdateAPIView):

    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs["chat_id"]
        participant_id = request.data["user_id"]
        chat = Chat.objects.get(id=chat_id)
        participant = Participant.objects.get(chat=chat, user_id=participant_id)

        if not chat.participants.filter(user=request.user, is_admin=True).exists():
            return Response(
                {"status": "Only admins can add other admins"},
                status=status.HTTP_403_FORBIDDEN,
            )

        participant.is_admin = True
        participant.save()
        return Response(
            {"status": "Participant added as admin"}, status=status.HTTP_200_OK
        )


class LeaveChatView(generics.DestroyAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        chat_id = self.kwargs["chat_id"]
        chat = Chat.objects.get(id=chat_id)
        participant = Participant.objects.get(chat=chat, user=request.user)

        if participant.is_admin:
            other_admins = chat.participants.filter(is_admin=True).exclude(
                user=request.user
            )
            if other_admins.exists():
                # Admins need to choose a new admin before leaving
                return Response(
                    {"status": "Select a new admin from remaining admins"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                # No other admins, chat will be deleted if there are no other participants
                chat.participants.remove(participant)
                if chat.participants.count() <= 1:
                    chat.delete()
                else:
                    return Response(
                        {"status": "No other admins, chat will be deleted"},
                        status=status.HTTP_200_OK,
                    )
        else:
            chat.participants.remove(participant)
            if chat.participants.count() == 0:
                chat.delete()

        return Response({"status": "Left the chat"}, status=status.HTTP_200_OK)


class PromoteAdminView(generics.UpdateAPIView):

    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs["chat_id"]
        user_id = request.data["user_id"]
        chat = Chat.objects.get(id=chat_id)
        user_to_promote = User.objects.get(id=user_id)

        if not chat.participants.filter(user=request.user, is_admin=True).exists():
            return Response(
                {"status": "Only admins can promote others"},
                status=status.HTTP_403_FORBIDDEN,
            )

        participant = Participant.objects.get(chat=chat, user=user_to_promote)
        participant.is_admin = True
        participant.save()
        return Response(
            {"status": "Participant promoted to admin"}, status=status.HTTP_200_OK
        )


class UpdateGroupNameView(generics.UpdateAPIView):

    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs["chat_id"]
        chat = Chat.objects.get(id=chat_id)

        if not chat.participants.filter(user=request.user, is_admin=True).exists():
            return Response(
                {"status": "Only admins can update the group name"},
                status=status.HTTP_403_FORBIDDEN,
            )

        chat.name = request.data["name"]
        chat.save()
        return Response({"status": "Group name updated"}, status=status.HTTP_200_OK)


class UpdateNicknameView(generics.UpdateAPIView):

    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs["chat_id"]
        chat = Chat.objects.get(id=chat_id)
        participant = Participant.objects.get(chat=chat, user=request.user)

        participant.nickname = request.data["nickname"]
        participant.save()
        return Response({"status": "Nickname updated"}, status=status.HTTP_200_OK)
