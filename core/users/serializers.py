# users/serializers.py

from rest_framework import serializers
from .models import CustomUser, UserProfile, Follow, Report

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['aura_points', 'aura_level', 'aura_sub_level', 'aura_color']

class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.ReadOnlyField(source='follower.username')
    followed = serializers.ReadOnlyField(source='followed.username')

    class Meta:
        model = Follow
        fields = ['follower', 'followed', 'followed_at']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report  # Make sure Report is properly referenced here
        fields = ['reported_user', 'report_type', 'description']
