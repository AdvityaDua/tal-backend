from .views import AddVideoLinkView, NotificationsView, RegisterView, TestView, LoginView, PasswordChange, OTPGenerationView, PasswordChangeWithOTP, VerifyMailView, TokenRefreshView, LogoutView, UserDetailsView, OTPValidationView, ResetPassword, FreezeVideoView
from django.urls import path

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('test/', TestView.as_view(), name='test'),
    path('login/', LoginView.as_view(), name='login'),
    path('password/change/', PasswordChange.as_view(), name='password_change'),
    path('otp/generate/', OTPGenerationView.as_view(), name='otp_generate'),
    path('otp/password/', PasswordChangeWithOTP.as_view(), name='otp_verify'),
    path('verify/email/', VerifyMailView.as_view(), name='verify_email'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('add-video/', AddVideoLinkView.as_view(), name='add_video_link'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('details/', UserDetailsView.as_view(), name='user_details'),
    path('validate/otp/', OTPValidationView.as_view(), name='validate_otp'),
    path('reset/password/', ResetPassword.as_view(), name='reset_password'),
    path('freeze-video/', FreezeVideoView.as_view(), name='freeze_video'),
]
