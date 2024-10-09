from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RandomActOfKindness, UserProfile, Badge, Notification, RAKClaim

@receiver(post_save, sender=RandomActOfKindness)
def handle_rak_post_save(sender, instance, created, **kwargs):
    # Handle aura points when RandomActOfKindness is completed
    if instance.completed_at and not instance.is_paid_forward:
        user_profile = instance.creator.userprofile
        user_profile.aura_points += instance.aura_points  # Use correct field name for aura points
        user_profile.calculate_level()  # Update aura level
        user_profile.save()

        # Award badges based on completed Random Acts of Kindness milestones
        completed_raks = RandomActOfKindness.objects.filter(creator=instance.creator, completed_at__isnull=False).count()
        if completed_raks >= 1:
            badge, _ = Badge.objects.get_or_create(
                name="First RAK Completed", 
                defaults={'description': "Awarded for completing your first Random Act of Kindness!"}
            )
            user_profile.user.badges.add(badge)

        if completed_raks >= 10:
            badge, _ = Badge.objects.get_or_create(
                name="10 RAKs Completed", 
                defaults={'description': "Awarded for completing 10 Random Acts of Kindness."}
            )
            user_profile.user.badges.add(badge)

        if completed_raks >= 50:
            badge, _ = Badge.objects.get_or_create(
                name="50 RAKs Completed", 
                defaults={'description': "Awarded for completing 50 Random Acts of Kindness."}
            )
            user_profile.user.badges.add(badge)

        if completed_raks >= 100:
            badge, _ = Badge.objects.get_or_create(
                name="100 RAKs Completed", 
                defaults={'description': "Awarded for completing 100 Random Acts of Kindness."}
            )
            user_profile.user.badges.add(badge)

    # Handle Pay It Forward logic
    if instance.is_paid_forward:
        # Ensure the RAK has been claimed
        if hasattr(instance, 'rak_claim'):
            claimant_profile = instance.rak_claim.claimant.userprofile
            bonus_points = 15  # Define bonus points for Pay It Forward
            claimant_profile.aura_points += bonus_points
            claimant_profile.calculate_level()
            claimant_profile.save()

    # Send notifications
    if instance.status == 'claimed':
        message = f"Your Random Act of Kindness has been claimed by {instance.rak_claim.claimant.username}."
        Notification.objects.create(recipient=instance.creator, message=message)

    if instance.completed_at:
        message = f"Your Random Act of Kindness has been completed."
        Notification.objects.create(recipient=instance.creator, message=message)
