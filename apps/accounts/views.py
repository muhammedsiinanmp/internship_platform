import logging

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.mixins import SuccessResponseMixin
from .models import User
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=["Auth"])
class RegisterView(SuccessResponseMixin, generics.CreateAPIView):
    """Register a new user (student or company)."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Issue tokens immediately on registration
        refresh = RefreshToken.for_user(user)
        profile_data = UserProfileSerializer(user).data
        return self.success_response(
            data={
                "user": profile_data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            message="Account created successfully.",
            http_status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Auth"])
class LoginView(TokenObtainPairView):
    """Login with email & password. Returns JWT tokens + user profile."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(
            {"status": "success", "message": "Login successful.", "data": data},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    """Blacklist the refresh token to log out."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"status": "error", "errors": {"refresh": "Refresh token is required."}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"status": "success", "message": "Logged out successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "errors": {"detail": "Invalid or expired token."}},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(tags=["Auth"])
class ProfileView(SuccessResponseMixin, generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return self.success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success_response(
            data=serializer.data, message="Profile updated successfully."
        )


@extend_schema(tags=["Auth"])
class ChangePasswordView(SuccessResponseMixin, APIView):
    """Change authenticated user's password."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        logger.info("Password changed for user %s", request.user.email)
        return self.success_response(message="Password changed successfully.")
