from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from .utils import get_aura_level

User = get_user_model()

class RAKPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rak_posts')

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

    description = models.TextField()
    media = models.FileField(upload_to='rak_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)
    aura_points = models.PositiveIntegerField(default=10)
    is_completed = models.DateTimeField(null=True)
    is_paid_forward = models.BooleanField(default=False)

    # Method to handle claiming of RAK
    def claim_rak(self, user):
        if self.status != 'open':
            raise ValueError("This RAK cannot be claimed.")
        self.status = 'claimed'
        self.save()

    # Awarding aura points for completed RAKs
    def award_aura_points(self):
        if self.status == 'completed':
            raise ValueError("Aura points have already been awarded for this RAK.")
        user_profile = self.user.userprofile
        user_profile.aura_points += self.aura_points
        user_profile.calculate_level()
        user_profile.save()

    # Handle Pay It Forward
    def pay_it_forward(self):
        if self.is_paid_forward:
            raise ValueError("This RAK has already been paid forward.")
        self.is_paid_forward = True
        self.save()
        self.award_pay_it_forward_bonus()

    def award_pay_it_forward_bonus(self):
        claimant_profile = self.claimed_rak.claimant.userprofile
        bonus_points = 15
        claimant_profile.aura_points += bonus_points
        claimant_profile.calculate_level()
        claimant_profile.save()

    # Method to update status with validation
    def update_status(self, new_status):
        if self.status == 'completed':
            raise ValueError("Cannot update a completed RAK.")
        self.status = new_status
        self.save()

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
    action_type = models.CharField(max_length=50)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_completed(self):
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    aura_points = models.PositiveIntegerField(default=0)

    def calculate_level(self):
        aura_info = get_aura_level(self.aura_points)
        self.aura_level = aura_info['main_level']
        self.aura_color = aura_info['color']
        self.save()

# Badge Model
class Badge(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Notification Model
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.message}"