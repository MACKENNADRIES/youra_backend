from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import RandomActOfKindness, UserProfile, Notification

# Get the correct User model
User = get_user_model()

@receiver(post_save, sender=RandomActOfKindness)
def handle_rak_post_save(sender, instance, created, **kwargs):
    # Handle aura points for the creator when RandomActOfKindness is completed
    if instance.completed_at and not instance.is_paid_forward:
        user_profile = instance.creator.userprofile
        previous_level = user_profile.aura_level  # Get the previous aura level
        user_profile.aura_points += instance.aura_points  # Add aura points to the creator
        user_profile.calculate_level()  # Update aura level
        user_profile.save()

        # Award badges based on completed Random Acts of Kindness milestones
        instance.award_badges(previous_level)

    # Handle Pay It Forward logic for the claimant
    if instance.is_paid_forward:
        if hasattr(instance, 'rak_claim'):
            claimant_profile = instance.rak_claim.claimant.userprofile
            bonus_points = 15  # Define bonus points for Pay It Forward
            claimant_profile.aura_points += bonus_points
            claimant_profile.calculate_level()
            claimant_profile.save()

    # NEW: Update aura points for the claimant when RAK is completed
    if instance.status == 'completed' and hasattr(instance, 'rak_claim'):
        claimant_profile = instance.rak_claim.claimant.userprofile
        aura_points_for_claimant = instance.aura_points // 2  # Give half of the aura points to the claimant
        claimant_profile.aura_points += aura_points_for_claimant
        claimant_profile.calculate_level()
        claimant_profile.save()

    # Send notifications
    if instance.status == 'claimed':
        message = f"Your Random Act of Kindness has been claimed by {instance.rak_claim.claimant.username}."
        Notification.objects.create(recipient=instance.creator, message=message)

    if instance.completed_at:
        message = f"Your Random Act of Kindness has been completed."
        Notification.objects.create(recipient=instance.creator, message=message)

    # Send notifications
    if instance.status == 'claimed':
        message = f"Your Random Act of Kindness has been claimed by {instance.rak_claim.claimant.username}."
        Notification.objects.create(recipient=instance.creator, message=message)

    if instance.completed_at:
        message = f"Your Random Act of Kindness has been completed."
        Notification.objects.create(recipient=instance.creator, message=message)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()

def send_notification(user, message):
    Notification.objects.create(recipient=user, message=message)
