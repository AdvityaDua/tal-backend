from django.urls import path
from .views import TicketListCreateView, TicketListForAdminUserView, MarkMessageAsRead, MessageView, MarkTicketAsClosed


urlpatterns = [
    path('create/', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('view/', TicketListForAdminUserView.as_view(), name='ticket-list-for-admin'),
    path('message/', MessageView.as_view(), name='message-view'),
    path('mark-as-read/', MarkMessageAsRead.as_view(), name='mark-message-as-read'),
    path('mark-as-closed/', MarkTicketAsClosed.as_view(), name='mark-ticket-as-closed'),
]