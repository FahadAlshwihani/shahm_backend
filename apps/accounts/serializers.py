from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "is_active", "password", "created_at"]

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
