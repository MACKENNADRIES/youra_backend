from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .models import RandomActOfKindness, RAKClaim, Report, PayItForward
from users.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist  


class RandomActOfKindnessSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')  # Owner field is read-only

    class Meta:
        model = RandomActOfKindness
        fields = ['id', 'description', 'media', 'created_at', 'owner', 'status', 'visibility', 'post_type', 'aura_points', 'completed_at']

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.media = validated_data.get('media', instance.media)
        instance.status = validated_data.get('status', instance.status)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.post_type = validated_data.get('post_type', instance.post_type)
        instance.aura_points = validated_data.get('aura_points', instance.aura_points)
        instance.completed_at = validated_data.get('completed_at', instance.completed_at)
        instance.save()
        return instance
    
class RAKClaimSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source='claimant.username')  # Read-only claimant
    rak_id = serializers.IntegerField(write_only=True)  # Allow rak_id in the request body

    class Meta:
        model = RAKClaim
        fields = ['id', 'rak_id', 'claimant', 'claimed_at', 'details']  # Include rak_id

    def create(self, validated_data):
        rak_id = validated_data.pop('rak_id')  # Get the rak_id from the validated data
        try:
            rak = RandomActOfKindness.objects.get(id=rak_id)
        except RandomActOfKindness.DoesNotExist:
            raise serializers.ValidationError("RAK not found.")

        # Ensure the claimant isn't the owner of the RAK
        if rak.owner == self.context['request'].user:
            raise serializers.ValidationError("You cannot claim your own RAK.")

        # Create the claim with the given RAK and claimant
        return RAKClaim.objects.create(rak=rak, claimant=self.context['request'].user, **validated_data)


class RAKClaimListSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source='claimant.username')  # Read-only claimant
    rak = serializers.PrimaryKeyRelatedField(queryset=RandomActOfKindness.objects.all())  # Add rak field here

    class Meta:
        model = RAKClaim
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details']

class RAKClaimDetailSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source='claimant.username')  # Read-only claimant
    rak = serializers.ReadOnlyField(source='rak.id')  # Read-only RAK post ID

    class Meta:
        model = RAKClaim
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reported_user', 'report_type', 'description']

class PayItForwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayItForward
        fields = ['original_rak', 'new_rak', 'pay_it_forward_by', 'created_at']

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username")
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Check if username exists in the database
        try:
            user = CustomUser.objects.get(username=username)
        except ObjectDoesNotExist:
            raise AuthenticationFailed("It seems like this account doesn't exist. Please check your username or register for a new account.", code='account_not_found')

        # If the username exists, check if the password is correct
        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if not user:
            raise AuthenticationFailed("Whoops! You've given us the incorrect details... To keep working on your aura with YOURA, check your username and password!", code='incorrect_password')

        attrs['user'] = user
        return attrs
