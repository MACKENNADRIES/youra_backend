from rest_framework import serializers
from .models import RAKPost, ClaimedRAK, ClaimAction

class RAKPostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')  # Owner field is read-only

    class Meta:
        model = RAKPost
        fields = ['id', 'description', 'media', 'created_at', 'owner', 'status', 'visibility', 'post_type', 'aura_points', 'is_completed']

class ClaimedRAKSerializer(serializers.ModelSerializer):
    rak = serializers.ReadOnlyField(source='rak.id')  # Add read-only field for related RAKPost
    claimant = serializers.ReadOnlyField(source='claimant.id')  # Claimant read-only

    class Meta:
        model = ClaimedRAK
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details']

class ClaimActionSerializer(serializers.ModelSerializer):
    claimed_rak = serializers.ReadOnlyField(source='claimed_rak.id')  # Add read-only field for related ClaimedRAK

    class Meta:
        model = ClaimAction
        fields = ['id', 'claimed_rak', 'action_type', 'description', 'completed', 'created_at', 'completed_at']
