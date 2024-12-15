from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from rak.choices import POST_TYPE_CHOICES, STATUS_CHOICES

User = get_user_model()


# This model is for everything RAK related........ is meant to be
class RandomActOfKindness(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(max_length=30)
    description = models.TextField(max_length=255)
    media = models.FileField(upload_to="rak_media/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="open")
    private = models.BooleanField(
        default=False, help_text="Private is only displayed to followers"
    )
    rak_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)
    action = models.TextField(
        max_length=255, help_text="Action or price requirement needed to fulfill RAK"
    )
    aura_points_value = models.PositiveIntegerField(default=10)
    completed_at = models.DateTimeField(null=True, blank=True)
    anonymous_rak = models.BooleanField(
        default=False, help_text="Keep created by anonymous"
    )
    # collaborators are people who are joining together to offer or request a rak
    allow_collaborators = models.BooleanField(
        default=False, help_text="Allow multiple collaborators "
    )
    # claimants are users who are joining together to claim a rak
    allow_claimants = models.BooleanField(
        default=False, help_text="Allow multiple claimants"
    )

    def __str__(self):
        return f"RAK: {self.title} by {self.created_by.username}"

    @property
    def is_paid_forward(self):
        """Returns true if this RAK was created with a Pay It Forward"""
        return self.pay_it_forwards.exists()

    def enable_collaborators(self):
        self.allow_claimants = True
        self.save()

    def claim_rak(self, user, comment="", anonymous_claimant=False):
        if self.status != "open" and not (
            self.allow_claimants and self.status == "in progress"
        ):
            raise ValueError(
                "This RAK cannot be claimed because it has already been claimed or completed."
            )

        if self.created_by == user:
            raise ValueError("You cannot claim your own RAK.")

        # Logic for if the user has already claimed a RAK - don't allow it
        existing_claim = self.claims.filter(claimer=user).exists()
        if existing_claim:
            raise ValueError("You have already claimed this RAK.")

        # Create a Claimant instance
        claimant = Claimant.objects.create(
            claimer=user,
            rak=self,
            comment=comment,
            anonymous_claimant=anonymous_claimant,
        )

        # Update RAK status
        if not self.allow_claimants:
            self.status = "in progress"
        elif self.status == "open":
            self.status = "in progress"
        self.save()

        return claimant

    def collaborate(self, user, comment="", anonymous_collaborator=False):
        if not self.allow_collaborators:
            raise ValueError("Collaborators are not allowed for this RAK.")

        if self.created_by == user:
            raise ValueError("You cannot collaborate on your own RAK.")

        # Check if particular user has already collaborated on this RAK
        if self.collabs.filter(collaborator=user).exists():
            raise ValueError("You have already collaborated on this RAK.")

        # Create a Collaborators instance
        collaborator = Collaborators.objects.create(
            collaborator=user,
            rak=self,
            comment=comment,
            anonymous_collaborator=anonymous_collaborator,
        )

        # Update RAK status
        if self.status == "open":
            self.status = "in progress"
            self.save()

        return collaborator

    def complete_rak(self):
        if self.status == "completed":
            return

        self.status = "completed"
        self.completed_at = timezone.now()
        self.save()

        # Award aura points to all claimants
        for claim in self.claims.all():
            claimant_profile = claim.claimer.userprofile
            claimant_profile.aura_points += self.aura_points_value
            claimant_profile.save()
            claimant_profile.calculate_level()  # Update aura level if necessary

    def send_notification(self, message):
        Notification.objects.create(recipient=self.created_by, message=message)


class Claimant(models.Model):
    claimer = models.ForeignKey(User, on_delete=models.CASCADE)
    rak = models.ForeignKey(
        RandomActOfKindness, on_delete=models.CASCADE, related_name="claims"
    )
    comment = models.TextField(max_length=255, help_text="Comment left by claimant")
    anonymous_claimant = models.BooleanField(
        default=False, help_text="Keep Claimant anonymous"
    )
    claimed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RAK claimed by {self.claimer.username} on {self.claimed_at}"


class Collaborators(models.Model):
    collaborator = models.ForeignKey(User, on_delete=models.CASCADE)
    rak = models.ForeignKey(
        RandomActOfKindness, on_delete=models.CASCADE, related_name="collabs"
    )
    comment = models.TextField(max_length=255, help_text="Comment left by collaborator")
    anonymous_collaborator = models.BooleanField(
        default=False, help_text="Keep Collaborator anonymous"
    )
    started_collabing_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RAK collaborated with {self.collaborator.username} on {self.started_collabing_at}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.message}"


class PayItForward(models.Model):
    original_rak = models.ForeignKey(
        RandomActOfKindness, on_delete=models.CASCADE, related_name="pay_it_forwards"
    )
    new_rak = models.OneToOneField(
        RandomActOfKindness,
        on_delete=models.CASCADE,
        related_name="pay_it_forward_instance",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def paid_forward_by(self):
        return self.new_rak.created_by

    def __str__(self):
        return f"Pay It Forward by {self.paid_forward_by.username} for {self.original_rak.title}"
