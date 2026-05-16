from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView

from accounts.models import Profile
from accounts.tokens import account_activation_token, password_reset_token
from accounts.utils import (
    ACTIVATION_SENT_MESSAGE,
    PASSWORD_RESET_SENT_MESSAGE,
    send_activation_email,
    send_password_reset_email,
)
from core.throttling import (
    ActivationRateThrottle,
    LoginRateThrottle,
    PasswordResetRateThrottle,
    RegistrationRateThrottle,
)

from . import serializers

User = get_user_model()


class RegistrationApiView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]
    serializer_class = serializers.RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_activation_email(user)
        return Response({"email": user.email}, status=status.HTTP_201_CREATED)


class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    serializer_class = serializers.CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "email": user.email,
            }
        )


class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    serializer_class = serializers.CustomTokenObtainPairSerializer


class CustomTokenBlacklistView(TokenBlacklistView):
    # TokenViewBase sets authentication_classes = () by default, so we must
    # restore it here for IsAuthenticated to work with DRF's global auth.
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [IsAuthenticated]


class ChangePasswordApiView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ChangePasswordSerializer

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        Token.objects.filter(user=user).delete()
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class ProfileApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        return get_object_or_404(self.get_queryset(), user=self.request.user)


class ActivationApiView(APIView):
    """Activate account via signed link from email (GET)."""

    permission_classes = [AllowAny]
    throttle_classes = [ActivationRateThrottle]

    def get(self, request, uidb64=None, token=None, *args, **kwargs):
        if not uidb64 or not token:
            return Response(
                {"detail": "Use POST with uid and token, or open the email link."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        user = self._get_user(uidb64, token)
        if user is None:
            return Response(
                {"detail": "Invalid or expired activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_verified:
            return Response({"detail": "Account is already verified."})
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        return Response({"detail": "Account verified successfully."})

    def post(self, request, *args, **kwargs):
        serializer = serializers.ActivationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._get_user(
            serializer.validated_data["uid"],
            serializer.validated_data["token"],
        )
        if user is None:
            return Response(
                {"detail": "Invalid or expired activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_verified:
            return Response({"detail": "Account is already verified."})
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        return Response({"detail": "Account verified successfully."})

    def _get_user(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
        if not account_activation_token.check_token(user, token):
            return None
        return user


class ActivationResendApiView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [ActivationRateThrottle]
    serializer_class = serializers.ActivationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        if user is not None and not user.is_verified:
            send_activation_email(user)
        return Response(ACTIVATION_SENT_MESSAGE, status=status.HTTP_200_OK)


class PasswordResetRequestApiView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    serializer_class = serializers.PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        if user is not None and user.is_verified:
            send_password_reset_email(user)
        return Response(PASSWORD_RESET_SENT_MESSAGE, status=status.HTTP_200_OK)


class PasswordResetConfirmApiView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def get(self, request, uidb64=None, token=None, *args, **kwargs):
        user = self._get_user(uidb64, token)
        if user is None:
            return Response(
                {"detail": "Invalid or expired password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "detail": "Link is valid. POST new password to this URL.",
                "uid": uidb64,
                "confirm_url": "/api/v1/password/reset/confirm/",
            }
        )

    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._get_user(
            serializer.validated_data["uid"],
            serializer.validated_data["token"],
        )
        if user is None:
            return Response(
                {"detail": "Invalid or expired password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        Token.objects.filter(user=user).delete()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )

    def _get_user(self, uidb64, token):
        if not uidb64 or not token:
            return None
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
        if not password_reset_token.check_token(user, token):
            return None
        return user
