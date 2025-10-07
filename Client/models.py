from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES = [('CLIENT', 'Client'),('FREELANCER', 'Freelancer')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES) 
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Gig(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=20, 
    choices=[('OPEN', 'Open'),('ASSIGNED','Assigned'),('CLOSED', 'Closed')], default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} — {self.status}"


class Bid(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    days = models.PositiveIntegerField()
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, 
    choices=[('PENDING','Pending'),('ACCEPTED','Accepted'),('REJECTED','Rejected')], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.freelancer.username} on {self.gig.title}"
    
class Order(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    agreed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    milestones = models.JSONField(blank=True)  # List of milestones with details
    status = models.CharField(max_length=20, choices=[('IN_PROGRESS','In Progress'),
    ('DELIVERED','Delivered'),('CLOSED','Closed')], default='IN_PROGRESS')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.gig.title} by {self.freelancer.username}"

class Attachment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Conversation(models.Model):
    client = models.ForeignKey(User, related_name='client_conversations', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, related_name='freelancer_conversations', on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, related_name='freelancer_reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.client.username} for {self.freelancer.username}"