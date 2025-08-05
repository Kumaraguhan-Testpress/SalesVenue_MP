from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    A custom user model that extends Django's built-in AbstractUser.

    This model adds additional fields for user-specific information
    like contact visibility, a phone number, and a profile picture.
    """

    contact_info_visibility = models.BooleanField(default=False, help_text="Whether the user's contact information is visible")
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="The user's contact phone number.")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, help_text="A profile picture for the user.")

    def __str__(self):
        return self.username
    
class Category(models.Model):
    """
    A model representing a Categories of Each advertisement posted by a user.
    """

    name = models.CharField(max_length=255, unique=True, help_text="The name of the category (e.g., 'Job', 'For Sale').")
    description = models.TextField(blank=True, null=True, help_text="A brief description of the category's purpose.")

    def __str__(self):
        return self.name  

class Ad(models.Model):
    """
    A model representing a single advertisement posted by a user.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ads', help_text="The user who created this ad.")
    title = models.CharField(max_length=255, help_text="The main title of the advertisement.")
    description = models.TextField(help_text="A detailed description of the ad's content.")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="The price of the item or service, if applicable.")
    location = models.CharField(max_length=255, help_text="The geographical location associated with the ad.")
    contact_info = models.CharField(max_length=255, help_text="Contact information for the ad, such as an email address or phone number.")
    contact_info_visible = models.BooleanField(default=False, help_text="Controls if the contact information is visible to all users or only the ad's owner.")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ads', help_text="The category this ad belongs to.")
    event_date = models.DateField(blank=True, null=True, help_text="The date of the event, applicable for 'Event' ads.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time the ad was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time the ad was last updated.")
    is_active = models.BooleanField(default=True, help_text="Indicates whether the ad is currently active and visible.")  

    def __str__(self):
        return self.title

    def is_visible_to_user(self, user):
        return self.contact_info_visible or user == self.user
    
class AdImage(models.Model):
    """
    A model to store multiple images for a single Ad.
    """

    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE, 
        related_name='images',
    )
    image = models.ImageField(
        upload_to='ad_images/',
        help_text="The image file for the ad."
    )
    
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for Ad: {self.ad.title}"


class Message(models.Model):
    """
    Represents a private message sent between two users regarding a specific ad.
    """

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages', help_text="The user who sent the message.")
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages', help_text="The user who is the recipient of the message.")
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='messages', help_text="The ad that this message is in reference to.")
    content = models.TextField(help_text="The content of the message.")
    sent_at = models.DateTimeField(auto_now_add=True, help_text="The date and time the message was sent.")
    read = models.BooleanField(default=False, help_text="Indicates whether the recipient has read the message.") 

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"
