from celery import shared_task

from django.utils import timezone
from django.contrib.auth import get_user_model

from datetime import timedelta

from auth_otp.users.models import UserDeletionPreSave
from auth_otp.otp.models import InviteOTP

User = get_user_model()


@shared_task
def check_user_deletions():

    thirty_days_ago = timezone.now() - timedelta(days=30)

    user_delete = UserDeletionPreSave.objects.filter(
        updated_at__lte=thirty_days_ago, is_verified=True
    )

    for deletion in user_delete:
        user_id = deletion.user_id
        user = User.objects.get(id=user_id)
        user.delete()
        invites = InviteOTP.objects.filter(email=user.email)
        for invite in invites:
            invite.delete()
        deletion.delete()

    return "User deletions processed successfully."
