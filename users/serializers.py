from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Address
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import password_validation
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
User = get_user_model()
class RegisterSerializer(serializers.ModelSerializer):  
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email','username','password','first_name','last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password =  validated_data['password'],
            first_name = validated_data.get('first_name',''),
            last_name = validated_data.get('last_name','')
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','username','first_name','last_name','phone_number')
        read_only_feilds = ('id','email','username')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['is_staff'] = self.user.is_staff
        data['username'] = self.user.username
        return data

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('user','created_at')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required = True,write_only=True)
    new_password = serializers.CharField(required =True,write_only = True,validators=[password_validation.validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password":"The new passwords do not match."})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    unidb64 = serializers.CharField(required= True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required =True,write_only = True,validators=[password_validation.validate_password])








