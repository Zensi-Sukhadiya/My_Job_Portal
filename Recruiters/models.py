from django.db import models
from django.conf import settings


class Recruiter(models.Model):

    COMPANY_SIZE_CHOICES = (
        ('1-10', '1–10 employees'),
        ('11-50', '11–50 employees'),
        ('51-200', '51–200 employees'),
        ('201-500', '201–500 employees'),
        ('500+', '500+ employees'),
    )

    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )

    # ── Core Relationship ────────────────────────────────────────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruiter'
    )

    # ── Basic Information ────────────────────────────────────────────────
    job_title       = models.CharField(max_length=150, blank=True, help_text="e.g. HR Manager, Talent Acquisition Lead")
    company_name    = models.CharField(max_length=255)
    company_website = models.URLField(blank=True)
    industry        = models.CharField(max_length=150, blank=True)
    company_size    = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    founded_year    = models.PositiveIntegerField(null=True, blank=True)
    company_description = models.TextField(blank=True)

    # ── Contact Information ──────────────────────────────────────────────
    official_email  = models.EmailField(blank=True)
    phone_number    = models.CharField(max_length=20, blank=True)
    address         = models.CharField(max_length=255, blank=True)
    city            = models.CharField(max_length=100, blank=True)
    state           = models.CharField(max_length=100, blank=True)
    country         = models.CharField(max_length=100, blank=True)
    linkedin_profile    = models.URLField(blank=True, help_text="Personal LinkedIn")
    company_linkedin    = models.URLField(blank=True, help_text="Company LinkedIn Page")
    twitter         = models.URLField(blank=True)
    facebook        = models.URLField(blank=True)

    # ── Company Branding ─────────────────────────────────────────────────
    company_logo    = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    cover_banner    = models.ImageField(upload_to='company_banners/', blank=True, null=True)
    company_video   = models.URLField(blank=True, help_text="YouTube or Vimeo link")

    # ── Verification ─────────────────────────────────────────────────────
    company_reg_number  = models.CharField(max_length=100, blank=True)
    gst_tax_id          = models.CharField(max_length=100, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )
    is_blue_tick = models.BooleanField(default=False)

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.company_name or self.user.email

    # ── Auto-calculated Public Stats ──────────────────────────────────────
    @property
    def total_jobs_posted(self):
        return self.user.jobs.count()

    @property
    def total_active_jobs(self):
        return self.user.jobs.filter(is_active=True).count()

    @property
    def total_applications(self):
        from Jobs.models import Application
        return Application.objects.filter(job__recruiter=self.user).count()

    @property
    def total_hires(self):
        from Jobs.models import Application
        return Application.objects.filter(job__recruiter=self.user, status='shortlisted').count()

class RecruiterSetting(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recruiter_settings')
    
    # 🔔 Notification Settings
    email_notifications = models.BooleanField(default=True)
    new_application_alert = models.BooleanField(default=True)
    shortlisted_candidate_alert = models.BooleanField(default=True)
    payment_invoice_alert = models.BooleanField(default=True)
    weekly_report_email = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # 🛠 Job Posting Defaults
    default_job_expiry_days = models.PositiveIntegerField(default=30)
    auto_approve_jobs = models.BooleanField(default=False)
    allow_remote_default = models.BooleanField(default=True)
    default_location = models.CharField(max_length=255, blank=True)
    default_salary_visibility = models.BooleanField(default=True)
    
    # 🌍 Privacy Settings
    show_profile_publicly = models.BooleanField(default=True)
    show_name_publicly = models.BooleanField(default=True)
    allow_direct_messaging = models.BooleanField(default=True)
    allow_candidate_save_company = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.user.email}"


class Subscription(models.Model):
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription_info')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.plan}"


class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recruiter_invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('paid', 'Paid'), ('pending', 'Pending'), ('failed', 'Failed')), default='paid')
    plan_name = models.CharField(max_length=50)

    def __str__(self):
        return self.invoice_number


class TeamMember(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('recruiter', 'Recruiter'),
        ('viewer', 'Viewer'),
    )
    company = models.ForeignKey('Recruiter', on_delete=models.CASCADE, related_name='team_members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recruiter')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.role} at {self.company.company_name}"
