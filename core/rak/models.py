from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

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
    completed_at = models.DateTimeField(null=True, blank=True)
    is_paid_forward = models.BooleanField(default=False)
    post_anonymously = models.BooleanField(default=False)
    allow_collaborators = models.BooleanField(default=False)  # Optional field to allow multiple claimants
    collaborators = models.ManyToManyField(User, related_name='rak_collaborators', blank=True)
    aura_points_awarded = models.BooleanField(default=False)
    # rak_claims = models.ManyToManyField('RAKClaim', related_name='raks', blank=True) # for collaborate 


    def enable_collaborators(self):
        self.allow_collaborators = True
        self.save()

    def add_collaborator(self, user):
        if self.allow_collaborators and user not in self.collaborators.all():
            self.collaborators.add(user)
            self.save()
        else:
            raise ValueError("Collaboration not allowed or user is already a collaborator.")

    def claim_rak(self, user):
        if self.status != 'open':
            raise ValueError("This RAK cannot be claimed because it has already been claimed or completed.")
        
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
        self.save()

        # Award aura points to the claimant if the RAK was claimed
        if hasattr(self, 'rak_claim'):
            claimant_profile = self.rak_claim.claimant.userprofile
            aura_points_for_claimant = self.aura_points 
            claimant_profile.aura_points += aura_points_for_claimant
            claimant_profile.calculate_level()  # Update aura level if necessary
            claimant_profile.save()

    def send_notification(self, message):
        Notification.objects.create(recipient=self.creator, message=message)

class RAKClaim(models.Model):
    rak = models.ForeignKey(RandomActOfKindness, on_delete=models.CASCADE, related_name='claims')  # Change the related_name
    claimant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rak_claims', null=True)
    claimed_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)
    claim_anonymously = models.BooleanField(default=False)

    def __str__(self):
        return f"RAK claimed by {self.claimant.username} on {self.claimed_at}"



class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.message}"

class PayItForward(models.Model):
    original_rak = models.ForeignKey(RandomActOfKindness, on_delete=models.CASCADE, related_name='pay_it_forwards')
    new_rak = models.OneToOneField(RandomActOfKindness, on_delete=models.CASCADE, related_name='pay_it_forward_instance')
    pay_it_forward_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pay It Forward by {self.pay_it_forward_by.username} for {self.original_rak.title}"
