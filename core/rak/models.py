from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .utils import get_aura_level
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class RandomActOfKindness(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rak_posts')

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('claimed', 'Claimed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    POST_TYPE_CHOICES = [
        ('offer', 'Offer'),
        ('request', 'Request'),
    ]

    title = models.TextField()
    description = models.TextField()
    media = models.FileField(upload_to='rak_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)
    aura_points = models.PositiveIntegerField(default=10)
    completed_at = models.DateTimeField(null=True)
    is_paid_forward = models.BooleanField(default=False)
    post_anonymously = models.BooleanField(default=False)
    allow_collaborators = models.BooleanField(default=False)  # Track if collaborators are allowed
    collaborators = models.ManyToManyField(User, blank=True, related_name='collaborative_raks')

    def enable_collaborators(self):
        self.allow_collaborators = True
        self.save()

    def add_collaborator(self, user):
        if self.allow_collaborators and user not in self.collaborators.all():
            self.collaborators.add(user)
            self.save()
        else:
            raise ValueError("Collaboration not allowed or user is already a collaborator.")

    # Method to handle claiming of RAK
    def claim_rak(self, user):
        if self.status != 'open':
            raise ValueError("This RAK cannot be claimed because it has already been claimed or completed.")
        
        # Prevent the owner from claiming their own RAK
        if self.creator == user:
            raise ValueError("You cannot claim your own RAK.")
        
        self.status = 'claimed'
        self.save()

        RAKClaim.objects.create(rak=self, claimant=user)

    def complete_rak(self):
        if self.status == 'completed':
            return
        self.status = 'completed'
        self.completed_at = timezone.now()
        previous_level = self.creator.userprofile.aura_level  # Track the previous level
        self.award_aura_points()  # Update aura points and level
        self.award_badges(previous_level)  # Pass previous level to badge awarding logic
        self.send_notification("Your Random Act of Kindness has been completed.")
        self.save()

    def award_aura_points(self):
        if self.status == 'completed':
            user_profile = self.creator.userprofile
            user_profile.aura_points += self.aura_points  # Award aura points
            user_profile.calculate_level()
            user_profile.save()
        else:
            raise ValueError("Aura points can only be awarded once the RAK is completed.")

# Badge awarding logic based on aura level milestones
    def award_badges(self, previous_level):
        # Get the current aura level after awarding points
        current_level = self.creator.userprofile.aura_level

        # Dictionary to map first occurrences of levels to badges
        badge_mapping = {
            "Generator": "First Generator Badge",
            "Manifesting Generator": "First Manifesting Generator Badge",
            "Projector": "First Projector Badge",
            "Manifestor": "First Manifestor Badge",
            "Reflector": "First Reflector Badge",
        }

        # Check if the user has just reached the first level of a new type
        if previous_level != current_level:
            if current_level in badge_mapping:
                # Notify the user about the badge
                self.send_notification(f"Congrats! You've earned the '{badge_mapping[current_level]}' badge.")


    # Sending notifications directly
    def send_notification(self, message):
        Notification.objects.create(recipient=self.creator, message=message)


    def award_pay_it_forward_bonus(self):
        claimant_profile = self.rak_claim.claimant.userprofile
        bonus_points = 15
        claimant_profile.aura_points += bonus_points
        claimant_profile.calculate_level()
        claimant_profile.save()

    def update_status(self, new_status):
        if self.status == 'completed':
            raise ValueError("Cannot update a completed RAK.")
        self.status = new_status
        self.save()


class RAKClaim(models.Model):
    rak = models.OneToOneField(RandomActOfKindness, on_delete=models.CASCADE, related_name='rak_claim')
    claimant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rak_claims')
    claimed_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"RAK claimed by {self.claimant.username} on {self.claimed_at}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    aura_points = models.PositiveIntegerField(default=0)
    aura_level = models.CharField(max_length=255, default="Initiator")
    aura_color = models.CharField(max_length=50, default="light yellow")

    def calculate_level(self):
        aura_info = get_aura_level(self.aura_points)
        self.aura_level = aura_info['main_level']
        self.aura_color = aura_info['light yellow']
        self.save()


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.message}"


class Report(models.Model):
    REPORT_TYPES = [
        ('inappropriate_rak', 'Inappropriate RAK'),
        ('inappropriate_comment', 'Inappropriate Comment'),
        ('unfulfilled_rak', 'Unfulfilled RAK'),
        ('user_block', 'User Block'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_against')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter} on {self.reported_user} for {self.report_type}"


class Block(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks_made')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)


class PayItForward(models.Model):
    original_rak = models.ForeignKey(RandomActOfKindness, on_delete=models.CASCADE, related_name='pay_it_forwards')
    new_rak = models.OneToOneField(RandomActOfKindness, on_delete=models.CASCADE, related_name='pay_it_forward_instance')
    pay_it_forward_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pay It Forward by {self.pay_it_forward_by.username} for {self.original_rak.title}"