from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'institute_name', 'team_members', 'phone_number', 'name', 'is_active', 'first_login', 'email_verified']
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)