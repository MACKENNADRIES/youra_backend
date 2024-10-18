# rak/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import RandomActOfKindness, Notification
from users.models import UserProfile

User = get_user_model()

@receiver(post_save, sender=RandomActOfKindness)
def handle_rak_post_save(sender, instance, created, **kwargs):
    if instance.status == 'completed' and not instance.is_paid_forward and not instance.aura_points_awarded:
        try:
            user_profile = instance.creator.userprofile
            previous_level = user_profile.aura_level
            user_profile.award_aura_points(instance.aura_points)
            user_profile.award_badges(previous_level)

            # Mark aura points as awarded
            instance.aura_points_awarded = True
            instance.save()

            # Send notification
            Notification.objects.create(
                recipient=instance.creator,
                message="Your Random Act of Kindness has been completed and aura points awarded."
            )
        except UserProfile.DoesNotExist:
            raise ValueError("User profile for the RAK creator does not exist.")

    # Handle Pay It Forward logic for the claimant
    if instance.is_paid_forward:
        if hasattr(instance, 'rak_claim'):
            claimant_profile = instance.rak_claim.claimant.userprofile
            bonus_points = 15  # Define bonus points for Pay It Forward
            claimant_profile.award_aura_points(bonus_points)
            # Optionally, award badges if level changes
            claimant_profile.award_badges(claimant_profile.aura_level)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            instance.userprofile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)
