from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RAKPost, UserProfile, Badge, Notification

@receiver(post_save, sender=RAKPost)
def update_aura_points(sender, instance, **kwargs):
    if instance.is_completed and not instance.is_paid_forward:
        user_profile = instance.user.userprofile
        user_profile.aura_points += instance.points
        user_profile.calculate_level()
        user_profile.save()

@receiver(post_save, sender=RAKPost)
def pay_it_forward_signal(sender, instance, **kwargs):
    if instance.is_paid_forward:
        claimant_profile = instance.claimant.userprofile
        bonus_points = 15  # Define bonus points for Pay It Forward
        claimant_profile.aura_points += bonus_points
        claimant_profile.calculate_level()
        claimant_profile.save()

@receiver(post_save, sender=RAKPost)
def award_rak_completion_badge(sender, instance, **kwargs):
    if instance.is_completed:
        user_profile = instance.user.userprofile
        completed_raks = RAKPost.objects.filter(user=instance.user, is_completed=True).count()

        # Milestone 1: First RAK Completed Badge
        badge, _ = Badge.objects.get_or_create(name="First RAK Completed", defaults={
            'description': "Awarded for completing your first Random Act of Kindness!"
        })
        user_profile.user.badges.add(badge)

        # Milestone 2: 10 RAKs Completed Badge
        if completed_raks >= 10:
            badge, _ = Badge.objects.get_or_create(name="10 RAKs Completed", defaults={
                'description': "Awarded for completing 10 Random Acts of Kindness."
            })
            user_profile.user.badges.add(badge)

        # Milestone 3: 50 RAKs Completed Badge
        if completed_raks >= 50:
            badge, _ = Badge.objects.get_or_create(name="50 RAKs Completed", defaults={
                'description': "Awarded for completing 50 Random Acts of Kindness."
            })
            user_profile.user.badges.add(badge)

        # Milestone 4: 100 RAKs Completed Badge
        if completed_raks >= 100:
            badge, _ = Badge.objects.get_or_create(name="100 RAKs Completed", defaults={
                'description': "Awarded for completing 100 Random Acts of Kindness."
            })
            user_profile.user.badges.add(badge)

@receiver(post_save, sender=RAKPost)
def award_pay_it_forward_badge(sender, instance, **kwargs):
    if instance.is_paid_forward:
        claimant_profile = instance.claimant.userprofile
        badge, _ = Badge.objects.get_or_create(name="Pay It Forward", defaults={
            'description': "Awarded for paying it forward after receiving a Random Act of Kindness."
        })
        claimant_profile.user.badges.add(badge)

@receiver(post_save, sender=UserProfile)
def award_aura_level_badges(sender, instance, **kwargs):
    aura_points = instance.aura_points

    # Milestone 1: Aura Level 1 - Initiator
    if aura_points >= 100 and aura_points < 200:
        badge, _ = Badge.objects.get_or_create(name="Aura Level 1 - Initiator", defaults={
            'description': "Awarded for reaching Aura Level 1 - Initiator."
        })
        instance.user.badges.add(badge)

    # Milestone 2: Aura Level 2 - Sustainer
    if aura_points >= 200 and aura_points < 300:
        badge, _ = Badge.objects.get_or_create(name="Aura Level 2 - Sustainer", defaults={
            'description': "Awarded for reaching Aura Level 2 - Sustainer."
        })
        instance.user.badges.add(badge)

    # Milestone 3: Aura Level 3 - Visionary
    if aura_points >= 300 and aura_points < 400:
        badge, _ = Badge.objects.get_or_create(name="Aura Level 3 - Visionary", defaults={
            'description': "Awarded for reaching Aura Level 3 - Visionary."
        })
        instance.user.badges.add(badge)

    # Milestone 4: Aura Level 4 - Creator
    if aura_points >= 400:
        badge, _ = Badge.objects.get_or_create(name="Aura Level 4 - Creator", defaults={
            'description': "Awarded for reaching Aura Level 4 - Creator."
        })
        instance.user.badges.add(badge)

@receiver(post_save, sender=RAKPost)
def create_notification_for_rak_claimed(sender, instance, created, **kwargs):
    if instance.status == 'claimed':
        message = f"Your Random Act of Kindness has been claimed by {instance.claimant.username}."
        Notification.objects.create(recipient=instance.user, message=message)

@receiver(post_save, sender=RAKPost)
def create_notification_for_rak_completed(sender, instance, **kwargs):
    if instance.is_completed:
        message = f"Your Random Act of Kindness has been completed."
        Notification.objects.create(recipient=instance.user, message=message)
