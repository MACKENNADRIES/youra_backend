# rak/serializers.py

from rest_framework import serializers
from .models import RandomActOfKindness, RAKClaim, PayItForward
from users.models import CustomUser
from users.serializers import UserProfileSerializer

class RandomActOfKindnessSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = RandomActOfKindness
        fields = ['id', 'title', 'description', 'media', 'created_at', 'owner', 'status', 'visibility', 'post_type', 'aura_points', 'completed_at']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
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
    claimant = serializers.ReadOnlyField(source='claimant.username')

    class Meta:
        model = RAKClaim
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details', 'claim_anonymously']

    def create(self, validated_data):
        return RAKClaim.objects.create(**validated_data)

    def get_claimant(self, obj):
        if obj.claim_anonymously:
            return "Anonymous"
        return obj.claimant.username

class RAKClaimListSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source='claimant.username')
    rak = serializers.PrimaryKeyRelatedField(queryset=RandomActOfKindness.objects.all())

    class Meta:
        model = RAKClaim
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details']

class RAKClaimDetailSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source='claimant.username')
    rak = serializers.ReadOnlyField(source='rak.id')

    class Meta:
        model = RAKClaim
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details']


class PayItForwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayItForward
        fields = ['original_rak', 'new_rak', 'pay_it_forward_by', 'created_at']

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
