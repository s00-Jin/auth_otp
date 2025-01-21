from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings


User = get_user_model()


class Chat(models.Model):

    name = models.CharField(max_length=255, blank=True, default="")
    is_group_chat = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name else f"Chat {self.id}"


class Participant(models.Model):

    chat = models.ForeignKey(
        Chat, related_name="participants", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=255, blank=True, default="")
    joined_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ("chat", "user")

    def __str__(self):
        return f"{self.user.username} in {self.chat.name}"

    def get_nickname(self):
        return self.nickname or self.user.username


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.nickname or self.sender.user.username} in chat {self.chat.id}"

    def save(self, *args, **kwargs):
        self.content = settings.CIPHER_SUITE.encrypt(self.content.encode()).decode()
        super().save(*args, **kwargs)

    def get_decrypted_content(self):
        return settings.CIPHER_SUITE.decrypt(self.content.encode()).decode()
