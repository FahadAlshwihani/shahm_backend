from rest_framework import serializers

from .models import User
from .roles import can_assign_role


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "is_active", "password", "created_at"]

    def _actor(self):
        return getattr(self.context.get("request"), "user", None)

    def validate_role(self, value):
        """Reject a role the caller does not outrank.

        Without this an ``admin`` could send ``role=super_admin`` and promote
        themselves or anyone else. The one exception is the disabled initial
        setup endpoint, which creates the very first account.
        """
        if self.context.get("bootstrap"):
            return value

        if not can_assign_role(self._actor(), value):
            raise serializers.ValidationError(
                "You may not assign this role."
            )

        return value

    def validate(self, attrs):
        actor = self._actor()
        role = attrs.get("role")

        if (
            role
            and self.instance is not None
            and actor is not None
            and getattr(actor, "pk", None) == self.instance.pk
            and role != self.instance.role
        ):
            raise serializers.ValidationError({
                "role": "You may not change your own role.",
            })

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        # 🔥 create_user يحتاج password — لذلك لازم نمرره
        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        # تحديث بيانات المستخدم
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
