from django.db import models

# Create your models here.

class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_solved = models.BooleanField(default=False)  # Corrected spelling
    solved_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
    

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
