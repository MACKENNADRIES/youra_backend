from rest_framework import serializers
from .models import RandomActOfKindness, RAKClaim, ClaimAction

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
    rak = serializers.ReadOnlyField(source='rak.id')  # Read-only RAK post ID

    class Meta:
        model = RAKClaim
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details']

    def update(self, instance, validated_data):
        # Update fields in the RAKClaim instance
        instance.details = validated_data.get('details', instance.details)
        instance.save()
        return instance

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

class ClaimActionSerializer(serializers.ModelSerializer):
    rak_claim = serializers.PrimaryKeyRelatedField(queryset=RAKClaim.objects.all())

    class Meta:
        model = ClaimAction
        fields = ['id', 'rak_claim', 'action_type', 'description', 'completed', 'created_at', 'completed_at']