"""
User serializers:
  - RegisterSerializer   : validate & create a new user account
  - LoginSerializer      : validate credentials and return the user object
  - UserSerializer       : read-only representation returned after auth
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration.
    `password` and `password2` are write-only — never returned in responses.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        label="Confirm password",
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2", "role")
        read_only_fields = ("id",)
        extra_kwargs = {
            "role": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # create_user hashes the password — never store plaintext
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", User.Role.USER),
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Validates email + password and returns the authenticated User instance.
    Not a ModelSerializer because we don't create/update anything here.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Django's authenticate() checks credentials and honours is_active
        user = authenticate(
            request=self.context.get("request"),
            username=email,   # USERNAME_FIELD is 'email', so this works
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}
            )

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only user representation returned after register / login.
    Sensitive fields (password) are intentionally excluded.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "date_joined")
        read_only_fields = fields
