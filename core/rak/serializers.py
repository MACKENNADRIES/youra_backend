from rest_framework import serializers
from .models import RandomActOfKindness, Claimant, Notification, PayItForward
from django.contrib.auth import get_user_model

User = get_user_model()


class ClaimantSerializer(serializers.ModelSerializer):
    claimer_username = serializers.SerializerMethodField()

    class Meta:
        model = Claimant
        fields = [
            "id",
            "claimer",
            "claimer_username",
            "rak",
            "comment",
            "anonymous_claimant",
            "claimed_at",
        ]
        extra_kwargs = {
            "claimer": {"read_only": True},
            "rak": {"read_only": True},
            "comment": {"required": True},
        }

    def get_claimer_username(self, obj):
        if obj.anonymous_claimant:
            return "Anon"
        else:
            return obj.claimer.username


class RandomActOfKindnessSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )
    claims = ClaimantSerializer(many=True, read_only=True)

    class Meta:
        model = RandomActOfKindness
        fields = [
            "id",
            "created_by",
            "created_by_username",
            "title",
            "description",
            "media",
            "created_at",
            "status",
            "private",
            "rak_type",
            "action",
            "aura_points_value",
            "completed_at",
            "anonymous_rak",
            "allow_collaborators",
            "claims",
        ]
        extra_kwargs = {
            "created_by": {"read_only": True},
            "status": {"read_only": True},
            "completed_at": {"read_only": True},
        }


class NotificationSerializer(serializers.ModelSerializer):
    recipient_username = serializers.CharField(
        source="recipient.username", read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "recipient_username",
            "message",
            "created_at",
            "is_read",
        ]
        extra_kwargs = {
            "recipient": {"read_only": True},
            "created_at": {"read_only": True},
            "is_read": {"read_only": True},
        }


class PayItForwardSerializer(serializers.ModelSerializer):
    original_rak = RandomActOfKindnessSerializer(read_only=True)
    new_rak = RandomActOfKindnessSerializer(read_only=True)
    paid_forward_by_username = serializers.CharField(
        source="paid_forward_by.username", read_only=True
    )

    class Meta:
        model = PayItForward
        fields = [
            "id",
            "original_rak",
            "new_rak",
            "created_at",
            "paid_forward_by_username",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
        }
