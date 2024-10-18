# rak/serializers.py

from rest_framework import serializers
from .models import RandomActOfKindness, RAKClaim, PayItForward 

class RandomActOfKindnessSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    rak_claim = serializers.SerializerMethodField()

    class Meta:
        model = RandomActOfKindness
        fields = ['id', 'title', 'description', 'media', 'created_at', 'owner', 'status', 'visibility', 'post_type', 'aura_points', 'completed_at', 'rak_claim']

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

    # Define the method to return the claim
    def get_rak_claim(self, obj):
        claim = RAKClaim.objects.filter(rak=obj).first()  # Get the claim for this RAK
        if claim:
            return RAKClaimDetailSerializer(claim).data  # Use detail serializer for claim info
        return None

class RAKClaimSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source='claimant.username')

    class Meta:
        model = RAKClaim
        fields = ['id', 'rak', 'claimant', 'claimed_at', 'details', 'claim_anonymously']

    def create(self, validated_data):
        rak = validated_data.get('rak')  # This will already be a RandomActOfKindness instance
        
        # Create the claim and set it on the RAK
        claim = RAKClaim.objects.create(**validated_data)
        rak.rak_claim = claim  # Ensure the RAK has the claim linked
        rak.save()  # Save the RAK with the linked claim

        return claim

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

