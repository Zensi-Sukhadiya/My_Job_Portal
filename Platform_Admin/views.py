from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg
from Accounts.models import User
from Jobs.models import Job, Application
from Students.models import Student

def is_platform_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')

@user_passes_test(is_platform_admin)
def admin_dashboard(request):
    # Statistics
    total_users = User.objects.count()
    total_students = User.objects.filter(role='student').count()
    total_recruiters = User.objects.filter(role='recruiter').count()
    total_jobs = Job.objects.count()
    pending_jobs = Job.objects.filter(is_approved=False).count()
    pending_recruiters = User.objects.filter(role='recruiter', is_approved=False).count()
    total_applications = Application.objects.count()

    # Recent activity for dashboard
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_recruiters': total_recruiters,
        'total_jobs': total_jobs,
        'pending_jobs': pending_jobs,
        'pending_recruiters': pending_recruiters,
        'total_applications': total_applications,
        'recent_jobs': recent_jobs,
        'recent_users': recent_users,
    }
    return render(request, 'platform_admin/dashboard.html', context)

@user_passes_test(is_platform_admin)
def manage_jobs(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'platform_admin/manage_jobs.html', {'jobs': jobs})

@user_passes_test(is_platform_admin)
def approve_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.is_approved = True
    job.approved_by = request.user
    job.save()
    messages.success(request, f"Job '{job.title}' has been approved.")
    return redirect('admin_manage_jobs')

@user_passes_test(is_platform_admin)
def reject_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    # Depending on business logic, we might just unapprove or delete
    # Here let's just mark it as unapproved and inactive
    job.is_approved = False
    job.is_active = False
    job.save()
    messages.warning(request, f"Job '{job.title}' has been rejected.")
    return redirect('admin_manage_jobs')

@user_passes_test(is_platform_admin)
def manage_recruiters(request):
    recruiters = User.objects.filter(role='recruiter').order_by('-created_at')
    return render(request, 'platform_admin/manage_recruiters.html', {'recruiters': recruiters})

@user_passes_test(is_platform_admin)
def approve_recruiter(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f"Recruiter '{user.name}' has been approved.")
    return redirect('admin_manage_recruiters')

@user_passes_test(is_platform_admin)
def manage_users(request):
    users = User.objects.exclude(id=request.user.id).order_by('-created_at')
    return render(request, 'platform_admin/manage_users.html', {'users': users})

@user_passes_test(is_platform_admin)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "blocked"
    messages.info(request, f"User '{user.username}' has been {status}.")
    return redirect('admin_manage_users')

@user_passes_test(is_platform_admin)
def view_all_applications(request):
    applications = Application.objects.all().order_by('-applied_at')
    return render(request, 'platform_admin/applications.html', {'applications': applications})


@user_passes_test(is_platform_admin)
def admin_analytics(request):
    """Advanced platform analytics with Chart.js-compatible data."""
    import json
    from django.db.models.functions import TruncMonth
    from Jobs.models import CompanyReview

    # Monthly signups (last 6 months)
    from django.utils import timezone
    from datetime import timedelta
    six_months_ago = timezone.now() - timedelta(days=180)

    monthly_users = (
        User.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    monthly_jobs = (
        Job.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    monthly_apps = (
        Application.objects.filter(applied_at__gte=six_months_ago)
        .annotate(month=TruncMonth('applied_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    def qs_to_chart(qs, label_field='month', value_field='count'):
        return {
            'labels': [entry[label_field].strftime('%b %Y') for entry in qs],
            'data': [entry[value_field] for entry in qs],
        }

    # Top companies by applications
    top_companies = (
        Job.objects.values('company')
        .annotate(apps=Count('applications'))
        .order_by('-apps')[:8]
    )

    # Application status breakdown
    status_counts = (
        Application.objects.values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Platform review stats
    total_reviews = CompanyReview.objects.count()
    avg_platform_rating = CompanyReview.objects.aggregate(avg=Avg('rating'))['avg'] or 0

    context = {
        'users_chart': json.dumps(qs_to_chart(monthly_users)),
        'jobs_chart': json.dumps(qs_to_chart(monthly_jobs)),
        'apps_chart': json.dumps(qs_to_chart(monthly_apps)),
        'top_companies': list(top_companies),
        'status_counts': list(status_counts),
        'total_reviews': total_reviews,
        'avg_platform_rating': round(avg_platform_rating, 1),
        # Summary cards
        'total_users': User.objects.count(),
        'total_jobs': Job.objects.count(),
        'total_applications': Application.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_recruiters': User.objects.filter(role='recruiter').count(),
    }
    return render(request, 'platform_admin/analytics.html', context)
