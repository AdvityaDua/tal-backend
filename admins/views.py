from rest_framework.views import APIView, Response, status
from rest_framework.permissions import AllowAny
from users.models import User
from users.serializers import UserSerializer
import os
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdminUser
from .models import Notification
from .serializers import NotificationSerializer


class NewAdminView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')
        access_code = request.data.get('access_code')
        if not email or not password or not name or not access_code:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if access_code != os.getenv("ADMIN_ACCESS_CODE"):
            return Response({"error": "Invalid access code"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.create_user(email=email, password=password, is_admin=True ,**request.data)
            return Response({"message": "Admin user created successfully", "user_id": user.email}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email, is_admin=True)
            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            refresh = RefreshToken.for_user(user)
            response = Response({'message': 'Login Successful', 'access_token': str(refresh.access_token), 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
            response.set_cookie('refresh_token', str(refresh), httponly=True, secure=True, samesite='Lax')
            return response
        except User.DoesNotExist:
            return Response({"error": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminChangePasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        access_code = request.data.get('access_code')
        
        if not email or not new_password or not access_code:
            return Response({"error": "Email, new password, and access code are required"}, status=status.HTTP_400_BAD_REQUEST)

        if access_code != os.getenv("ADMIN_ACCESS_CODE"):
            return Response({"error": "Invalid access code"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(email=email, is_admin=True)
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access_token": access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TeamsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        teams = User.objects.filter(is_admin=False)
        serializer = UserSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, team_id):
        try:
            team = User.objects.get(email=team_id, is_admin=False)
            serializer = UserSerializer(team)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Team member not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def patch(self, request, team_id):
        try:
            team = User.objects.get(email=team_id, is_admin=False)
            serializer = UserSerializer(team, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

    def delete(self, request, team_id):
        try:
            team = User.objects.get(email=team_id, is_admin=False)
            team.delete()
            return Response({"message": "Team member deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class NotificationsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Assuming notifications are stored in a model called Notification
        notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            return Response({"message": "Notification deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
            serializer = NotificationSerializer(notification, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
