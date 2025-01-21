from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views.users import (
    LoginView,
    CustomTokenObtainPairView,
    SimpleGetView,
    RegisterCreateAPIView,
    ForgotPasswordOTPSent,
    ForgotPassword,
    ChangePasswordOTPSent,
    ChangePasswordAPIView,
    UserDeletionAPIView,
    VerifyUserDeletionAPIView,
)
from .views.otp import InviteCreateAPIView, OTPCheckView
from .views.chats import (
    ChatCreateView,
    ChatListView,
    ParticipantListView,
    MessageListView,
    UserChatsView,
    AddParticipantView,
    PendingApprovalListView,
    ApproveParticipantView,
    AddAdminView,
    LeaveChatView,
    PromoteAdminView,
    UpdateGroupNameView,
    UpdateNicknameView,
)

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path(
        "login/otp-verify", CustomTokenObtainPairView.as_view(), name="login_otp_verify"
    ),
    path("login/refresh/", TokenRefreshView.as_view(), name="login_token_refresh"),
    path("register/", RegisterCreateAPIView.as_view(), name="register"),
    path(
        "forgot-password/OTP/",
        ForgotPasswordOTPSent.as_view(),
        name="forgot_password_otp",
    ),
    path("forgot-password/", ForgotPassword.as_view(), name="forgot_password"),
    path(
        "change-password/OTP/",
        ChangePasswordOTPSent.as_view(),
        name="change_password_otp",
    ),
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="change_password",
    ),
    path(
        "user-deletion/create/",
        UserDeletionAPIView.as_view(),
        name="user_deletion_record_creation",
    ),
    path(
        "user-deletion/verify/",
        VerifyUserDeletionAPIView.as_view(),
        name="user_deletion_verification",
    ),
    path("otp-check/", OTPCheckView.as_view(), name="otp_check"),
    path("invite-code/email/", InviteCreateAPIView.as_view(), name="invite-code_email"),
    path("simple-get/", SimpleGetView.as_view(), name="simple_get"),
    # chat endpoints
    path("chats/", ChatCreateView.as_view(), name="chat-create"),
    path("chats/list/", ChatListView.as_view(), name="chat-list"),
    path(
        "chats/<int:chat_id>/participants/",
        ParticipantListView.as_view(),
        name="participant-list",
    ),
    path(
        "chats/<int:chat_id>/messages/", MessageListView.as_view(), name="message-list"
    ),
    path("user/chats/", UserChatsView.as_view(), name="user-chats"),
    path(
        "chats/<int:chat_id>/participants/add/",
        AddParticipantView.as_view(),
        name="add-participant",
    ),
    path(
        "chats/<int:chat_id>/participants/pending/",
        PendingApprovalListView.as_view(),
        name="pending-approval",
    ),
    path(
        "chats/<int:chat_id>/participants/approve/",
        ApproveParticipantView.as_view(),
        name="approve-participant",
    ),
    path("chats/<int:chat_id>/admins/add/", AddAdminView.as_view(), name="add-admin"),
    path("chats/<int:chat_id>/leave/", LeaveChatView.as_view(), name="leave-chat"),
    path(
        "chats/<int:chat_id>/promote/", PromoteAdminView.as_view(), name="promote-admin"
    ),
    path(
        "chats/<int:chat_id>/update-name/",
        UpdateGroupNameView.as_view(),
        name="update-group-name",
    ),
    path(
        "chats/<int:chat_id>/update-nickname/",
        UpdateNicknameView.as_view(),
        name="update-nickname",
    ),
]
