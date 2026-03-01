"""
Auth views:
  POST /api/auth/register/       — create account, return tokens
  POST /api/auth/login/          — authenticate, return tokens
  POST /api/auth/logout/         — blacklist refresh token
  POST /api/auth/token/refresh/  — exchange refresh for new access token
"""

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.core.exceptions import api_response
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

logger = logging.getLogger(__name__)


def _get_tokens_for_user(user) -> dict:
    """Generate a JWT access + refresh token pair for the given user."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView):
    """
    Register a new user account.
    Returns the user profile and JWT tokens on success.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = _get_tokens_for_user(user)
        data = {
            "user": UserSerializer(user).data,
            "tokens": tokens,
        }
        logger.info("New user registered: %s", user.email)
        return api_response(data, "Account created successfully.", status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Authenticate with email + password.
    Returns JWT tokens and the user profile on success.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        tokens = _get_tokens_for_user(user)
        data = {
            "user": UserSerializer(user).data,
            "tokens": tokens,
        }
        logger.info("User logged in: %s", user.email)
        return api_response(data, "Login successful.")


class LogoutView(APIView):
    """
    Blacklist the provided refresh token, invalidating that session.
    The access token remains valid until it expires (short-lived by design).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return api_response(
                message="Refresh token is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return api_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        logger.info("User logged out: %s", request.user.email)
        return api_response(message="Logout successful.")
