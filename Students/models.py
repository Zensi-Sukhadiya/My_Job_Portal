from django.db import models
from django.conf import settings

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    headline = models.CharField(max_length=255, blank=True, help_text="e.g. Python Developer | Django Enthusiast")
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    
    # Social Links
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    
    # Legacy fields
    college = models.CharField(max_length=200, blank=True)
    skills_text = models.TextField(blank=True, help_text="Legacy skills text field") 
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Skill(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.student.user.username})"

class Education(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_currently_studying = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Education Records"

    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Experience(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.role} at {self.company}"

class Project(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class Certification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Language(models.Model):
    PROFICIENCY_CHOICES = (
        ('elementary', 'Elementary'),
        ('limited', 'Limited Working'),
        ('professional', 'Professional Working'),
        ('full', 'Full Professional'),
        ('native', 'Native / Bilingual'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES, default='professional')

    def __str__(self):
        return self.name