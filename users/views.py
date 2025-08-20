from rest_framework.views import APIView, Response, status
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, OTP
from rest_framework_simplejwt.tokens import RefreshToken
import random
from .utils import send_verification_email
from admins.models import Notification
from admins.serializers import NotificationSerializer
from django.db.models import Q


class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully", "user_id": user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            
            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            refresh = RefreshToken.for_user(user)
            response = Response({'message': 'Login Successful', 'access_token': str(refresh.access_token), 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
            response.set_cookie('refresh_token', str(refresh), httponly=True, secure=True, samesite='Lax')
            return response
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class OTPGenerationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.filter(user=user).delete()
            OTP.objects.create(user=user, otp_code=otp_code)
            if send_verification_email(user, otp_code):
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordChange(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        
        if not user.first_login:
            old_password = request.data.get('old_password')
            if not user.check_password(old_password):
                return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.first_login = False
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

class VerifyMailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        
        if not email or not otp_code:
            return Response({"error": "Email and OTP code are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.get(user=user, otp_code=otp_code)
            
            if not otp.verify_otp(otp_code):
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
            user.email_verified = True
            user.save()
            otp.delete()  
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except OTP.DoesNotExist:
            return Response({"error": "OTP not found"}, status=status.HTTP_404_NOT_FOUND)


class PasswordChangeWithOTP(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')
        
        if not email or not otp_code or not new_password:
            return Response({"error": "Email, OTP code, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.get(user=user, otp_code=otp_code)
            
            if not otp.verify_otp(otp_code):
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            otp.delete()  
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except OTP.DoesNotExist:
            return Response({"error": "OTP not found"}, status=status.HTTP_404_NOT_FOUND)


class TestView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"message": "Test successful"}, status=status.HTTP_200_OK)

class AddVideoLinkView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        video_link = request.data.get('video_link')
        
        if not video_link:
            return Response({"error": "Video link is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.video_link = video_link
        user.save()
        return Response({"message": "Video link added successfully"}, status=status.HTTP_200_OK)
    
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            user_id = refresh.payload.get('user_id')
            user = User.objects.get(id=user_id)
            return Response({"access_token": access_token, 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        notifications = Notification.objects.filter(Q(user=str(request.user)) | Q(user="all"))
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        return response


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)