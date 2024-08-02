from celery import shared_task

from django.utils import timezone
from django.contrib.auth import get_user_model

from datetime import timedelta

from auth_otp.users.models import UserDeletionPreSave

User = get_user_model()


@shared_task
def check_user_deletions():

    thirty_days_ago = timezone.now() - timedelta(days=30)

    user_delete = UserDeletionPreSave.objects.filter(
        updated_at__lte=thirty_days_ago, is_verified=True
    )

    user_ids = user_delete.values_list("user_id", flat=True)
    users = User.objects.filter(id__in=user_ids)

    for user in users:
        user.delete()

    return "Data deleted successfully"
