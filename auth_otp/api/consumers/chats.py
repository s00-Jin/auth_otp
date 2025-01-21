# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from auth_otp.chats.models import Chat, ChatLines


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.user = self.scope["user"]

        # Check if the user is a participant in the chat
        chat = await self.get_chat()
        if chat is None or self.user not in chat.participants.all():
            await self.close()
            return

        # Join chat room group
        self.room_group_name = f"chat_{self.chat_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave chat room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        # Save the message to the database
        chat = await self.get_chat()
        if chat:
            chat_line = await self.save_message(chat, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": chat_line.message,
                    "sender": chat_line.sender.username,
                    "timestamp": str(chat_line.timestamp),
                },
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def get_chat(self):
        # Retrieve the chat
        try:
            return await Chat.objects.prefetch_related("participants").aget(
                id=self.chat_id
            )
        except Chat.DoesNotExist:
            return None

    async def save_message(self, chat, message):
        chat_line = ChatLines.objects.create(
            chat=chat, sender=self.user, message=message
        )
        return chat_line
