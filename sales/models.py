from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    """
    A custom user model that extends Django's built-in AbstractUser.

    This model adds additional fields for user-specific information
    like contact visibility, a phone number, and a profile picture.
    """
    contact_info_visibility = models.BooleanField(default=False, help_text="Whether the user's contact information is visible")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.username
    
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class AdType(models.TextChoices):

    """
    A class-based enumeration for the types of advertisements available.
    """
    JOB = 'job', 'Job'
    PET = 'pet', 'Pet Corner'
    SALE = 'sale', 'For Sale'
    SERVICE = 'service', 'Service'
    EVENT = 'event', 'Event'

class Ad(models.Model):
    
    """
    A model representing a single advertisement posted by a user.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    contact_info_visible = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ads')
    ad_type = models.CharField(max_length=20, choices=AdType.choices, default=AdType.SALE)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  

    def __str__(self):
        return self.title

    def is_visible_to_user(self, user):
        return self.contact_info_visible or user == self.user
    

class Message(models.Model):

    """
    Represents a private message sent between two users regarding a specific ad.
    """
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False) 

    def __str__(self):
        """Returns a string representation of the message."""
        return f"Message from {self.sender.username} to {self.recipient.username}"