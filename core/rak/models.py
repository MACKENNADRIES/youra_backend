from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model  # Import the User model
from users.models import CustomUser  # Import user from users app (if needed)
from .utils import get_aura_level

User = get_user_model()  # Define User to refer to the current user model

class RAKPost(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    is_paid_forward = models.BooleanField(default=False)  # Track if this is a Pay It Forward
    # other fields...
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rak_posts'
    )
    description = models.TextField()
    media = models.FileField(upload_to='rak_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)
    aura_points = models.PositiveIntegerField(default=10)
    is_completed = models.DateTimeField(null=True)

    def complete_rak(self):
        if self.status == 'completed':
            return
        self.status = 'completed'
        self.is_completed = timezone.now()
        self.save()

    def award_aura_points(self):
        user_profile = self.user.userprofile
        user_profile.aura_points += 10  # Add aura points for completing a RAK
        user_profile.calculate_level()  # Calculate new aura level
        user_profile.save()

    def pay_it_forward(self):
        if not self.is_paid_forward:
            self.is_paid_forward = True
            self.save()
            self.award_pay_it_forward_bonus()

    def award_pay_it_forward_bonus(self):
        claimant_profile = self.claimant.userprofile
        bonus_points = 15  # Add bonus points for paying it forward
        claimant_profile.aura_points += bonus_points
        claimant_profile.calculate_level()
        claimant_profile.save()

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('claimed', 'Claimed'),
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

class ClaimedRAK(models.Model):
    rak = models.OneToOneField(RAKPost, on_delete=models.CASCADE, related_name='claimed_rak')
    claimant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='claimed_raks'
    )
    claimed_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

class ClaimAction(models.Model):
    claimed_rak = models.ForeignKey(ClaimedRAK, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=50)  # E.g., 'send_money', 'tutor_session', 'deliver_item'
    description = models.TextField()  # Description of the action
    completed = models.BooleanField(default=False)  # Status of the action
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_completed(self):
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    aura_points = models.PositiveIntegerField(default=0)

    def calculate_level(self):
        aura_info = get_aura_level(self.aura_points)
        self.aura_level = aura_info['main_level']
        self.aura_color = aura_info['color']
        self.save()