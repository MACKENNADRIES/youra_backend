from rest_framework import serializers
from .models import RAKPost, ClaimedRAK, ClaimAction

class RAKPostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')  # Owner field is read-only

    class Meta:
        model = RAKPost
        fields = ['id', 'description', 'media', 'created_at', 'owner', 'status', 'visibility', 'post_type', 'aura_points', 'is_completed']

    def update(self, instance, validated_data):
        # Update each field individually, using the current value if a new value is not provided
        instance.description = validated_data.get('description', instance.description)
        instance.media = validated_data.get('media', instance.media)
        instance.status = validated_data.get('status', instance.status)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.post_type = validated_data.get('post_type', instance.post_type)
        instance.aura_points = validated_data.get('aura_points', instance.aura_points)
        instance.is_completed = validated_data.get('is_completed', instance.is_completed)
        
        # Save the instance with the updated values
        instance.save()
        return instance

class ClaimedRAKListSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source='claimant.username')  # Read-only claimant
    rak = serializers.ReadOnlyField(source='rak.id')  # Read-only RAK post ID

    class Meta:
        model = ClaimedRAK
        fields = ['id', 'rak', 'claimant', 'claimed_at']

class ClaimedRAKDetailSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source='claimant.username')  # Read-only claimant
    rak = serializers.ReadOnlyField(source='rak.id')  # Read-only RAK post ID

    class Meta:
        model = ClaimedRAK
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details']


class ClaimActionSerializer(serializers.ModelSerializer):
    claimed_rak = serializers.ReadOnlyField(source='claimed_rak.id')  # Add read-only field for related ClaimedRAK

    class Meta:
        model = ClaimAction
        fields = ['id', 'claimed_rak', 'action_type', 'description', 'completed', 'created_at', 'completed_at']
