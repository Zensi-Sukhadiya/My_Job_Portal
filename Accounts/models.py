from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    profile_views = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # SaaS / Account Controls
    is_email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Billing
    SUBSCRIPTION_PLANS = (
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    )
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLANS, default='free')
    subscription_status = models.CharField(max_length=20, default='active')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.email

    @property
    def profile_completion(self):
        """Calculates the profile completion percentage."""
        fields = ['name', 'email', 'profile_picture']
        total = len(fields)
        filled = 0
        
        for field in fields:
            if getattr(self, field):
                filled += 1
        
        # Additional checks based on role
        if self.role == 'recruiter':
            try:
                profile = self.recruiter 
                if profile.company_name: filled += 1
                if profile.company_website: filled += 1
                total += 2
            except:
                pass
        elif self.role == 'student':
            try:
                profile = self.student_profile
                # Core student fields
                if profile.headline: filled += 1
                if profile.bio: filled += 1
                if profile.location: filled += 1
                if profile.phone: filled += 1
                if profile.resume: filled += 1
                total += 5
                
                # Check related models
                if profile.education.exists(): filled += 1
                if profile.experience.exists(): filled += 1
                if profile.projects.exists(): filled += 1
                if profile.skills.exists(): filled += 1
                total += 4
            except Exception as e:
                pass
                
        return int((filled / total) * 100) if total > 0 else 0


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    icon_class = models.CharField(max_length=50, default='fa-solid fa-circle-dot')
    link = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"

class Notification(models.Model):
    TYPES = (
        ('app_status', 'Application Status'),
        ('msg', 'New Message'),
        ('interview', 'Interview Invitation'),
        ('profile_view', 'Profile Viewed'),
        ('job_alert', 'Job Alert'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}"
