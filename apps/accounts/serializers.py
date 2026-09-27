from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model, password_validation
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.constants import Department, Degree, Role
from apps.recruiters.models import RecruiterProfile
from apps.students.models import StudentProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "full_name", "role", "date_joined")
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=80, allow_blank=True, required=False, default="")
    role = serializers.ChoiceField(choices=[Role.STUDENT, Role.RECRUITER])
    registration_number = serializers.CharField(required=False, allow_blank=True)
    department = serializers.ChoiceField(choices=Department.choices, required=False)
    degree = serializers.ChoiceField(choices=Degree.choices, required=False)
    graduation_year = serializers.IntegerField(required=False)
    cgpa = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)
    designation = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate_password(self, value: str) -> str:
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["role"] == Role.STUDENT:
            required = ["registration_number", "department", "degree", "graduation_year", "cgpa"]
            missing = [f for f in required if not attrs.get(f)]
            if missing:
                raise serializers.ValidationError(
                    {field: "This field is required for students." for field in missing}
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data["role"]
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ""),
            role=role,
        )
        if role == Role.STUDENT:
            StudentProfile.objects.create(
                user=user,
                registration_number=validated_data["registration_number"],
                department=validated_data["department"],
                degree=validated_data["degree"],
                graduation_year=validated_data["graduation_year"],
                cgpa=validated_data["cgpa"],
            )
        else:
            RecruiterProfile.objects.create(
                user=user,
                designation=validated_data.get("designation", ""),
            )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"].lower(),
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=10)

    def validate_new_password(self, value: str) -> str:
        password_validation.validate_password(value, user=self.context["request"].user)
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "Current password is incorrect."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


def tokens_for(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}
