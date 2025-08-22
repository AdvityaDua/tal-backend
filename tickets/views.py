from rest_framework.views import Response, APIView, status
from .serializers import TicketSerializer, TicketDetailSerializer, MessageSerializer
from .models import Ticket, Message
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class TicketListCreateView(APIView):
    def get(self, request):
        if request.user.is_admin:
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.filter(user=request.user)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_admin:
            return Response({"error": "Permission denied. Only users can make a new ticket."}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        message = data.pop('message', None)
        data['user'] = request.user.pk
        serializer = TicketSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            if message:
                Message.objects.create(ticket=serializer.instance, sender_type="user", message=message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TicketListForAdminUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "is_admin", False):
            tickets = Ticket.objects.prefetch_related("messages").all()
        else:
            tickets = Ticket.objects.prefetch_related("messages").filter(user=request.user)

        serializer = TicketDetailSerializer(tickets, many=True)
        return Response(serializer.data)



class MessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        ticket_id = data.pop("ticket_id", None)
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if ticket.status == "closed":
            return Response({"detail": "Cannot send message. Ticket is closed."}, status=status.HTTP_400_BAD_REQUEST)

        data['sender_type'] = "admin" if request.user.is_admin else "user"
        if not ticket_id or not Ticket.objects.filter(id=ticket_id).exists():
            return Response({"detail": "Invalid ticket ID."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MessageSerializer(data=data)
         
        data['ticket'] = Ticket.objects.get(id=ticket_id).id
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Message sent successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class MarkMessageAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message_id = request.data.get("message_id")
        if not message_id:
            return Response({"detail": "message_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        message = get_object_or_404(Message, id=message_id)

        # Optional: permission check
        if message.sender_type == "user" and not getattr(request.user, "is_admin", False):
            return Response({"detail": "You cannot mark admin messages as read."}, status=status.HTTP_403_FORBIDDEN)

        if message.sender_type == "admin" and message.ticket.user != request.user:
            return Response({"detail": "You cannot mark other user's messages as read."}, status=status.HTTP_403_FORBIDDEN)

        message.is_read = True
        message.save()

        return Response({"message": "Message marked as read."}, status=status.HTTP_200_OK)


class MarkTicketAsClosed(APIView):
    def post(self, request):
        ticket_id = request.data.get("ticket_id")
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.status = "closed"
        ticket.save()
        return Response({"message": "Ticket marked as closed."}, status=status.HTTP_200_OK)