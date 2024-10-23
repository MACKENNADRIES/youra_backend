# rak/serializers.py

from rest_framework import serializers
from .models import RandomActOfKindness, RAKClaim, PayItForward


class RandomActOfKindnessSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")
    rak_claim = serializers.SerializerMethodField()

    class Meta:
        model = RandomActOfKindness
        fields = [
            "id",
            "title",
            "description",
            "media",
            "created_at",
            "owner",
            "status",
            "visibility",
            "post_type",
            "aura_points",
            "completed_at",
            "claims",
            "rak_claim" "allow_collaborators",
        ]

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.media = validated_data.get("media", instance.media)
        instance.status = validated_data.get("status", instance.status)
        instance.visibility = validated_data.get("visibility", instance.visibility)
        instance.post_type = validated_data.get("post_type", instance.post_type)
        instance.aura_points = validated_data.get("aura_points", instance.aura_points)
        instance.completed_at = validated_data.get(
            "completed_at", instance.completed_at
        )
        instance.save()
        return instance

    # Define the method to return the claim
    def get_rak_claim(self, obj):
        claim = RAKClaim.objects.filter(rak=obj).first()  # Get the claim for this RAK
        if claim:
            return RAKClaimDetailSerializer(
                claim
            ).data  # Use detail serializer for claim info
        return None


class RAKClaimSerializer(serializers.ModelSerializer):
    claimant = (
        serializers.SerializerMethodField()
    )  # Updated to handle anonymous claims dynamically

    class Meta:
        model = RAKClaim
        fields = ["id", "rak", "claimant", "claimed_at", "details", "claim_anonymously"]

    # Method to return 'Anonymous' if claim_anonymously is True
    def get_claimant(self, obj):
        if obj.claim_anonymously:
            return "Anonymous"
        return obj.claimant.username  # If not anonymous, return username

    def create(self, validated_data):
        rak = validated_data.get("rak")  # Get the RAK instance

        # Create the claim without directly linking it in the RAK
        claim = RAKClaim.objects.create(**validated_data)

        # Save the RAK to update its status (if needed)
        rak.save()

        return claim


class RAKClaimListSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source="claimant.username")
    rak = serializers.PrimaryKeyRelatedField(queryset=RandomActOfKindness.objects.all())

    class Meta:
        model = RAKClaim
        fields = ["id", "rak", "claimant", "claimed_at", "details"]


class RAKClaimDetailSerializer(serializers.ModelSerializer):
    claimant = serializers.ReadOnlyField(source="claimant.username")
    rak = serializers.ReadOnlyField(source="rak.id")

    class Meta:
        model = RAKClaim
        fields = ["id", "rak", "claimant", "claimed_at", "details"]


class PayItForwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayItForward
        fields = ["original_rak", "new_rak", "pay_it_forward_by", "created_at"]
