from django.db import models
from django.contrib.auth.models import AbstractUser
from users.utils import get_aura_level  # Ensure this utility function is in users/utils.py
from django.conf import settings

class CustomUser(AbstractUser):
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    aura_points = models.PositiveIntegerField(default=0)
    aura_level = models.CharField(max_length=255, default="Initiator")
    aura_sub_level = models.CharField(max_length=255, default="Initiator")
    aura_color = models.CharField(max_length=50, default="light yellow")
    points_from_claiming = models.IntegerField(default=0)
    points_from_pay_it_forward = models.IntegerField(default=0)
    points_from_offers = models.IntegerField(default=0)

    def calculate_level(self):
        aura_info = get_aura_level(self.aura_points)
        self.aura_level = aura_info['main_level']
        self.aura_sub_level = aura_info['sub_level']
        self.aura_color = aura_info.get('color', 'light yellow')
        self.save()

    def award_aura_points(self, points):
        self.aura_points += points
        self.calculate_level()
        self.save()

    def award_badges(self, previous_level):
        current_level = self.aura_level
        badge_mapping = {
            "Generator": "First Generator Badge",
            "Manifesting Generator": "First Manifesting Generator Badge",
            "Projector": "First Projector Badge",
            "Manifestor": "First Manifestor Badge",
            "Reflector": "First Reflector Badge",
        }
        if previous_level != current_level and current_level in badge_mapping:
            from rak.models import Notification  # Avoid circular import
            Notification.objects.create(
                recipient=self.user,
                message=f"Congrats! You've earned the '{badge_mapping[current_level]}' badge."
            )

    def __str__(self):
        return f"UserProfile for {self.user.username}"

class Block(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocks_made')
    blocked_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} blocked {self.blocked_user}"

class Report(models.Model):
    REPORT_TYPES = [
        ('inappropriate_rak', 'Inappropriate RAK'),
        ('inappropriate_comment', 'Inappropriate Comment'),
        ('unfulfilled_rak', 'Unfulfilled RAK'),
        ('user_block', 'User Block'),
    ]

    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_against')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter} on {self.reported_user} for {self.report_type}"

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
