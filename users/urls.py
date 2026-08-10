from django.urls import path,include
from .views import RegisterView,UserProfileView,AddressViewSet,ChangePasswordView,PasswordResetConfirmView,PasswordResetRequestView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"addresses",AddressViewSet,basename='address')


urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('profile/',UserProfileView.as_view(),name='profile'),

    #about password
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    path('', include(router.urls)),

]
