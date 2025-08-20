from django.urls import path
from .views import NewAdminView, AdminLoginView, AdminChangePasswordView, TokenRefreshView, TeamView, NotificationsView

urlpatterns = [
    path('register/', NewAdminView.as_view(), name='new_admin'),
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('change-password/', AdminChangePasswordView.as_view(), name='admin_change_password'),
    path('refresh/', TokenRefreshView.as_view(), name='admin_refresh_token'),
    path('teams/', TeamView.as_view(), name='admin_teams'),
    path('teams/<int:team_id>/', TeamView.as_view(), name='admin_team_detail'),
    path('notifications/', NotificationsView.as_view(), name='admin_notifications'),
    path('notifications/<int:notification_id>/', NotificationsView.as_view(), name='admin_notification_detail'),
]