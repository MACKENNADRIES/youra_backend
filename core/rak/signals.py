# rak/signals.py

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
        # Case 1: RAK is an offer, award points to the creator
        if instance.post_type == 'offer':
            user_profile = instance.creator.userprofile
            previous_level = user_profile.aura_level
            user_profile.aura_points += instance.aura_points  # Add aura points to the creator
            user_profile.calculate_level()
            user_profile.save()
            instance.award_badges(previous_level)  # Award badges for completed RAKs

        # Case 2: RAK is a request, no points for the owner, claimant gets points
        elif instance.post_type == 'request' and instance.status == 'completed' and hasattr(instance, 'rak_claim'):
            claimant_profile = instance.rak_claim.claimant.userprofile
            aura_points_for_claimant = instance.aura_points
            claimant_profile.aura_points += aura_points_for_claimant  # Give full points to the claimant
            claimant_profile.calculate_level()
            claimant_profile.save()

    # Case 3: If Pay It Forward is completed, award points to the original RAK owner (requester)
    if instance.is_paid_forward and instance.status == 'completed' and instance.post_type == 'request':
        original_rak_owner_profile = instance.creator.userprofile
        aura_points_for_owner = instance.aura_points  # The original requester now gets the points
        original_rak_owner_profile.aura_points += aura_points_for_owner
        original_rak_owner_profile.calculate_level()
        original_rak_owner_profile.save()

    # Handle notifications
    if instance.status == 'claimed':
        Notification.objects.create(
            recipient=instance.creator, 
            message=f"Your Random Act of Kindness has been claimed by {instance.rak_claim.claimant.username}."
        )
    if instance.completed_at:
        Notification.objects.create(
            recipient=instance.creator, 
            message=f"Your Random Act of Kindness has been completed."
        )


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            instance.userprofile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)
