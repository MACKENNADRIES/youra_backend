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
    user = CustomUserSerializer(read_only=True)  #NESTING!!!!!!!!!!!!!!!
    points_from_claiming_percentage = serializers.SerializerMethodField()
    points_from_pay_it_forward_percentage = serializers.SerializerMethodField()
    points_from_offers_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'user',  # This now includes id, username, email, first_name, last_name from CustomUser
            'aura_points', 
            'aura_level', 
            'aura_sub_level', 
            'aura_color',
            'points_from_claiming', 
            'points_from_pay_it_forward', 
            'points_from_offers',
            'points_from_claiming_percentage',  # New percentage field for claiming
            'points_from_pay_it_forward_percentage',  # New percentage field for Pay It Forward
            'points_from_offers_percentage'  # New percentage field for offers
        ]

    # Helper function to calculate the percentage
    def calculate_percentage(self, part, total):
        if total == 0:  # Prevent division by zero
            return 0
        return (part / total) * 100

    # Method to calculate the percentage of points acquired from claiming
    def get_points_from_claiming_percentage(self, obj):
        return self.calculate_percentage(obj.points_from_claiming, obj.aura_points)

    # Method to calculate the percentage of points acquired from Pay It Forward
    def get_points_from_pay_it_forward_percentage(self, obj):
        return self.calculate_percentage(obj.points_from_pay_it_forward, obj.aura_points)

    # Method to calculate the percentage of points acquired from offers
    def get_points_from_offers_percentage(self, obj):
        return self.calculate_percentage(obj.points_from_offers, obj.aura_points)

class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username")
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        from django.core.exceptions import ObjectDoesNotExist
        from django.contrib.auth import authenticate
        from rest_framework.exceptions import AuthenticationFailed
        from users.models import CustomUser

        username = attrs.get('username')
        password = attrs.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except ObjectDoesNotExist:
            raise AuthenticationFailed(
                "It seems like this account doesn't exist. Please check your username or register for a new account.",
                code='account_not_found'
            )

        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if not user:
            raise AuthenticationFailed(
                "Whoops! You've given us the incorrect details... To keep working on your aura with YOURA, check your username and password!",
                code='incorrect_password'
            )

        attrs['user'] = user
        return attrs


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
