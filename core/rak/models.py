from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .utils import get_aura_level

User = get_user_model()

class RandomActOfKindness(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
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
    completed_at = models.DateTimeField(null=True)
    is_paid_forward = models.BooleanField(default=False)

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
        self.award_aura_points()
        self.save()

    def award_aura_points(self):
        if self.status == 'completed':
            user_profile = self.creator.userprofile
            user_profile.aura_points += self.aura_points  # Award aura points
            user_profile.calculate_level()
            user_profile.save()
        else:
            raise ValueError("Aura points can only be awarded once the RAK is completed.")

    # Handle Pay It Forward
    def pay_it_forward(self):
        if self.is_paid_forward:
            raise ValueError("This RAK has already been paid forward.")
        self.is_paid_forward = True
        self.save()
        self.award_pay_it_forward_bonus()

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

def save(self, *args, **kwargs):
    # Only apply the validation check for new RAKs, not when updating existing ones
    if self._state.adding:  # This checks if the instance is being created
        if RandomActOfKindness.objects.filter(
            creator=self.creator, 
            description=self.description, 
            created_at__gte=timezone.now() - timedelta(minutes=10)
        ).exists():
            raise ValueError("You have already posted a similar RAK recently.")
    
    super().save(*args, **kwargs)

class PayItForward(models.Model):
    original_rak = models.OneToOneField(RandomActOfKindness, on_delete=models.CASCADE, related_name='original_rak')
    new_rak = models.ForeignKey(RandomActOfKindness, on_delete=models.CASCADE, related_name='pay_it_forward_rak')
    bonus_points = models.PositiveIntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)

class RAKClaim(models.Model):
    rak = models.OneToOneField(RandomActOfKindness, on_delete=models.CASCADE, related_name='rak_claim')
    claimant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rak_claims')
    claimed_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"RAK claimed by {self.claimant.username} on {self.claimed_at}"


class ClaimAction(models.Model):
    rak_claim = models.ForeignKey(RAKClaim, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=50)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_completed(self):
        if self.completed:
            raise ValueError("This action is already completed.")
        self.completed = True
        self.completed_at = timezone.now()
        self.save()
        

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    aura_points = models.PositiveIntegerField(default=0)
    aura_level = models.CharField(max_length=255, default="Beginner")  # Add this field
    aura_color = models.CharField(max_length=50, default="Blue")  # Add this field

    def calculate_level(self):
        aura_info = get_aura_level(self.aura_points)
        self.aura_level = aura_info['main_level']
        self.aura_color = aura_info['color']
        self.save()


class Badge(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.message}"
