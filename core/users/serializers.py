from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},  # Ensure email is required for user creation
        }

    def create(self, validated_data):
        # Use create_user method to ensure password is hashed
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # Remove the password from the validated data before updating
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)

        # If a new password is provided, set it securely
        if password:
            instance.set_password(password)
            instance.save()

        return instance
