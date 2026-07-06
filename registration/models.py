from django.db import models


# Create your models here.
class UserProfile(models.Model):
    """Model representing a user profile."""
    id = models.AutoField(
        primary_key=True, unique=True, 
        editable=False, auto_created=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    entered_by_id = models.CharField(max_length=100)

    class Meta:
        """Meta options for the UserProfile model."""
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["created_at"]

    def __str__(self) -> str:
        """String representation of the UserProfile model."""
        return f'{self.username} - {self.email}'
