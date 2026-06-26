from django.conf import settings
from django.db import models
from django.utils.text import slugify


# Create your models here.
class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full-time', 'Full Time'),
        ('part-time', 'Part-time'),
        ('intern', 'Internship'),
        ('remote', 'Remote'),
        ('contract', 'Contract'),
    )

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    category = models.ForeignKey('Jobs.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    salary = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='job_logos/', blank=True, null=True)
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    deadline = models.DateField(null=True, blank=True)
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_jobs'
    )

    def __str__(self):
        return f"{self.title} at {self.company}"



class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    )

    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name='applications', null=True, blank=True)    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    
    # Form Fields
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    min_salary = models.CharField(max_length=50, blank=True)
    max_salary = models.CharField(max_length=50, blank=True)
    graduate = models.CharField(max_length=50, blank=True)
    skills = models.TextField(blank=True)
    
    resume = models.FileField(upload_to='application_resumes/')
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = f"{self.first_name} {self.last_name}" if self.first_name else self.student.user.username if self.student else "Unknown"
        return f"{name}'s application for {self.job.title}"



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=100, blank=True, help_text="FontAwesome icon class")
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class SavedJob(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'job')
        verbose_name_plural = "Saved Jobs"

    def __str__(self):
        return f"{self.student.user.username} saved {self.job.title}"


class InterviewSchedule(models.Model):
    FORMAT_CHOICES = (
        ('video', 'Video Call'),
        ('phone', 'Phone Call'),
        ('in_person', 'In Person'),
        ('technical', 'Technical Test'),
    )
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='interview')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='video')
    location_or_link = models.CharField(max_length=512, blank=True, help_text="Zoom link or office address")
    notes = models.TextField(blank=True, help_text="Instructions for the candidate")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview for {self.application} on {self.scheduled_at.strftime('%b %d, %Y %H:%M')}"


class CompanyReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    company_recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_reviews',
        limit_choices_to={'role': 'recruiter'}
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    pros = models.TextField(blank=True, help_text="What you liked")
    cons = models.TextField(blank=True, help_text="What could be better")
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company_recruiter', 'reviewer')
        verbose_name_plural = "Company Reviews"

    def __str__(self):
        return f"{self.rating}★ for {self.company_recruiter.username} by {self.reviewer.username}"
