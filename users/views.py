from django.shortcuts import render
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import generics
from .serializers import RegisterSerializer,UserProfileSerializer,CustomTokenObtainPairSerializer,AddressSerializer,ChangePasswordSerializer,PasswordResetConfirmSerializer,PasswordResetRequestSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .models import Address


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user = self.request.user).order_by('-is_default','-created_at')

    def perform_create(self, serializer):
        return serializer.save(user = self.request.user)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = ChangePasswordSerializer(data = request.data)

        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password":"Current password is incorrect"})
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message":"Password changed successfully"})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = PasswordResetRequestSerializer(data = request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                reset_link = f"http://localhost:5173/reset-password/{uid}/{token}/"

                send_mail(
                    subject='Password recovery request',
                    message=f'Click on the link below to reset your password:\n{reset_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list= [ user.email],
                )
            return Response({"message":"If the email exists in the system, a recovery link was sent."})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = PasswordResetConfirmSerializer(data = request.data)

        if serializer.is_valid():
            uidb64 = serializer.validated_data['uidb64']
            token = serializer.validated_data['token']
            password = serializer.validated_data['new_password']

            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)

            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response({"message":"Password changed successfully"},status=status.HTTP_200_OK)
            else :
                return Response({"error":"The link is expired or invalid."},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            


