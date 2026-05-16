from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import Profile, User


class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=255, write_only=True)
    username = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password1"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password1"):
            raise serializers.ValidationError({"detail": "Passwords do not match."})
        try:
            validate_password(attrs.get("password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password1", None)
        email = validated_data["email"]
        if not validated_data.get("username"):
            validated_data["username"] = email.split("@")[0][:20]
        validated_data.setdefault("is_verified", False)
        return User.objects.create_user(**validated_data)


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        if not email or not password:
            raise serializers.ValidationError(
                _('Must include "email" and "password".'),
                code="authorization",
            )
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            raise serializers.ValidationError(
                _("Unable to log in with provided credentials."),
                code="authorization",
            )
        if not user.is_verified:
            raise serializers.ValidationError(
                {"detail": "Account is not verified. Check your email."},
                code="authorization",
            )
        attrs["user"] = user
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError(
                {"detail": "Account is not verified. Check your email."}
            )
        data["email"] = self.user.email
        data["user_id"] = self.user.id
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError({"detail": "Passwords do not match."})
        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "email", "first_name", "last_name", "description")


class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            attrs["user"] = User.objects.get(email=email)
        except User.DoesNotExist:
            attrs["user"] = None
        return attrs


class ActivationConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            attrs["user"] = User.objects.get(email=email)
        except User.DoesNotExist:
            attrs["user"] = None
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError({"detail": "Passwords do not match."})
        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs
