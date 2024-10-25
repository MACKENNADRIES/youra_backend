# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import RandomActOfKindness, Notification
from users.models import UserProfile

User = get_user_model()


@receiver(post_save, sender=RandomActOfKindness)
def handle_rak_post_save(sender, instance, created, **kwargs):
    # Only award aura points if the RAK is completed and it's not a Pay It Forward action
    if instance.completed_at and not instance.is_paid_forward:
        # Case 1: RAK is an offer, award points to the created_by
        if instance.rak_type == "offer":
            user_profile = instance.created_by.userprofile
            user_profile.aura_points += (
                instance.aura_points
            )  # Add aura points to the created_by
            user_profile.points_from_offers += (
                instance.aura_points
            )  # Track points from offers
            user_profile.save()

        # Case 2: RAK is a request, no points for the owner, claimant gets points
        elif instance.rak_type == "request" and instance.status == "completed":
            for claim in instance.claims.all():
                claimant_profile = claim.claimer.userprofile
                claimant_profile.points_from_claiming += instance.aura_points_value
                claimant_profile.save()

    # Case 3: If Pay It Forward is completed, award points to the original RAK owner (requester)
    if (
        instance.is_paid_forward
        and instance.status == "completed"
        and instance.rak_type == "request"
    ):
        original_rak_owner_profile = instance.created_by.userprofile
        aura_points_for_owner = (
            instance.aura_points
        )  # The original requester now gets the points
        original_rak_owner_profile.aura_points += aura_points_for_owner
        original_rak_owner_profile.points_from_pay_it_forward += (
            aura_points_for_owner  # Track points from Pay It Forward
        )
        original_rak_owner_profile.save()

    # Handle notifications
    if instance.status == "claimed":
        for claim in instance.claims.all():
            Notification.objects.create(
                recipient=instance.created_by,
                message=f"Your Random Act of Kindness has been claimed by {claim.claimer.username}.",
            )
    if instance.completed_at:
        Notification.objects.create(
            recipient=instance.created_by,
            message=f"Your Random Act of Kindness has been completed.",
        )


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Ensure the UserProfile exists
        UserProfile.objects.get_or_create(user=instance)
