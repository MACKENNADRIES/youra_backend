from django.db import models

# This section is for all things relating to a rak (Random ACt of Kindness)

from django.db import models
from django.utils import timezone
from users.models import CustomUser  # Import user from users app

class RAKPost(models.Model):
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
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rak_posts')
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

class ClaimedRAK(models.Model):
    rak = models.OneToOneField(RAKPost, on_delete=models.CASCADE, related_name='claimed_rak')
    claimant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='claimed_raks')
    claimed_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)  # Details on how the RAK will be fulfilled

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

class PayItForward(models.Model):
    original_rak = models.OneToOneField(RAKPost, on_delete=models.CASCADE, related_name='original_rak')
    new_rak = models.ForeignKey(RAKPost, on_delete=models.CASCADE, related_name='pay_it_forward_rak')
    bonus_points = models.PositiveIntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
