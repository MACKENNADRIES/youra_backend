from django.db import models
from django.contrib.auth.models import AbstractUser
from users.utils import (
    get_aura_level,
)  # Ensure this utility function is in users/utils.py
from django.conf import settings
from simple_history.models import HistoricalRecords


class CustomUser(AbstractUser):
    def __str__(self):
        return self.username


from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    aura_points = models.PositiveIntegerField(default=0)
    aura_level = models.CharField(max_length=255, default="Initiator")
    aura_sub_level = models.CharField(max_length=255, default="Initiator")
    aura_color = models.CharField(max_length=50, default="#50C878")
    points_from_claiming = models.IntegerField(default=0)
    points_from_pay_it_forward = models.IntegerField(default=0)
    points_from_offers = models.IntegerField(default=0)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    history = HistoricalRecords()

    def calculate_level(self):
        aura_info = get_aura_level(self.aura_points)
        self.aura_level = aura_info["level"]
        self.aura_color = aura_info.get("glowColor", "#50C878")
        self.save()

    def award_aura_points(self, points):
        self.aura_points += points
        self.calculate_level()
        self.save()


def award_badges(self, previous_points):
    # Get the previous and current aura levels
    previous_level_info = get_aura_level(previous_points)
    current_level_info = get_aura_level(self.aura_points)

    # Check if the level has changed
    if previous_level_info and current_level_info:
        previous_level = previous_level_info["level"]
        current_level = current_level_info["level"]

        if previous_level != current_level:
            # Define badge mapping for each aura level
            badge_mapping = {
                "Initiator": "First Initiator Badge",
                "Sustainer": "First Sustainer Badge",
                "Visionary": "First Visionary Badge",
                "Creator": "First Creator Badge",
                "Innovator": "First Innovator Badge",
                "Accelerator": "First Accelerator Badge",
                "Transformer": "First Transformer Badge",
                "Healer": "First Healer Badge",
                "Orchestrator": "First Orchestrator Badge",
                "Harmoniser": "First Harmoniser Badge",
            }

            # Award badge if the current level has a badge
            if current_level in badge_mapping:
                badge_name = badge_mapping[current_level]

                # Avoid circular import
                from rak.models import Notification

                # Create a notification or handle badge logic here
                Notification.objects.create(
                    user=self.user,
                    title=f"Congratulations on achieving {current_level}!",
                    message=f"You've earned the {badge_name}. Keep up the great work!",
                )

                # You could also add logic to save the badge in the user's profile
                self.badges.add(badge_name)
                self.save()

    def __str__(self):
        return f"UserProfile for {self.user.username}"


class Block(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="blocks_made"
    )
    blocked_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="blocked_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} blocked {self.blocked_user}"


class Report(models.Model):
    REPORT_TYPES = [
        ("inappropriate_rak", "Inappropriate RAK"),
        ("inappropriate_comment", "Inappropriate Comment"),
        ("unfulfilled_rak", "Unfulfilled RAK"),
        ("user_block", "User Block"),
    ]

    reporter = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="reports_made"
    )
    reported_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="reports_against"
    )
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Report by {self.reporter} on {self.reported_user} for {self.report_type}"
        )


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
