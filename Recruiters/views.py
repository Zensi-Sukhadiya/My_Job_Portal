from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import recruiter_required
from django.contrib import messages
from Jobs.models import Job, Application
from Accounts.models import User
from My_Job_Portal.utils import log_activity, send_email_notification
from django.utils import timezone
from datetime import timedelta
import random


@login_required(login_url='recruiter_login')
@recruiter_required
def recruiter_dashboard(request):
    
    # Date Filtering
    days = int(request.GET.get('days', 30))
    now = timezone.now()
    start_date = now - timedelta(days=days)
    prev_start_date = start_date - timedelta(days=days)

    user_jobs = Job.objects.filter(recruiter=request.user)
    
    # Stats for current period
    total_jobs = user_jobs.count()
    active_jobs = user_jobs.filter(is_active=True).count()
    
    apps_current = Application.objects.filter(
        job__recruiter=request.user, 
        applied_at__gte=start_date
    ).count()
    
    apps_prev = Application.objects.filter(
        job__recruiter=request.user, 
        applied_at__gte=prev_start_date,
        applied_at__lt=start_date
    ).count()

    # Growth Calculation
    if apps_prev > 0:
        apps_growth = int(((apps_current - apps_prev) / apps_prev) * 100)
    else:
        apps_growth = 100 if apps_current > 0 else 0

    # Views Growth (Mocked/Estimated since we don't have historical view logs)
    total_job_views = sum(job.views for job in user_jobs)
    views_growth = random.randint(5, 15) # Mocked historical growth

    # General Stats
    total_applications = Application.objects.filter(job__recruiter=request.user)
    total_apps_count = total_applications.count()
    shortlisted_apps = total_applications.filter(status='shortlisted').count()
    shortlist_rate = int((shortlisted_apps / total_apps_count * 100)) if total_apps_count > 0 else 0

    total_students = User.objects.filter(role='student').count()
    recent_jobs = user_jobs.order_by('-created_at')[:5]

    latest_applications = total_applications.select_related(
        'job',
        'student__user'
    ).order_by('-applied_at')[:5]

    # Chart Data
    job_names = [job.title for job in recent_jobs]
    application_counts = [job.applications.count() for job in recent_jobs]

    # Activity Timeline
    activities = request.user.activities.all().order_by('-timestamp')[:6]

    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_apps_count,
        'total_job_views': total_job_views,
        'apps_growth': apps_growth,
        'views_growth': views_growth,
        'shortlist_rate': shortlist_rate,
        'total_students': total_students,
        'recent_jobs': recent_jobs,
        'latest_applications': latest_applications,
        'job_names': job_names,
        'application_counts': application_counts,
        'activities': activities,
        'selected_days': days,
    }

    return render(request, 'recruiters/recruiter_dashboard.html', context)



@login_required(login_url='recruiter_login')
@recruiter_required
def manage_jobs(request):
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    return render(request, 'recruiters/manage_jobs.html', {'jobs': jobs})



@login_required(login_url='recruiter_login')
@recruiter_required
def manage_applications(request):
    job_id = request.GET.get('job')
    status = request.GET.get('status')
    
    applications = Application.objects.filter(job__recruiter=request.user).select_related('job', 'student__user')
    
    if job_id:
        applications = applications.filter(job_id=job_id)
    if status:
        applications = applications.filter(status=status)
        
    applications = applications.order_by('-applied_at')
    
    # For filter dropdowns
    jobs = Job.objects.filter(recruiter=request.user)
    status_choices = Application.STATUS_CHOICES

    return render(request, 'recruiters/manage_applications.html', {
        'applications': applications,
        'jobs': jobs,
        'status_choices': status_choices,
        'selected_job': int(job_id) if job_id else None,
        'selected_status': status
    })



@login_required(login_url='recruiter_login')
@recruiter_required
def update_application_status(request, app_id, status):
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    if status in dict(Application.STATUS_CHOICES):
        application.status = status
        application.save()

        log_activity(
            request.user,
            "Status Updated",
            f"Updated application for {application.student.user.name} to {status}",
            "fa-solid fa-clipboard-check"
        )

        messages.success(request, f"Application status updated to {status}.")
        
        # Create Student Notification
        if application.student:
            from Accounts.models import Notification
            status_labels = dict(Application.STATUS_CHOICES)
            Notification.objects.create(
                user=application.student.user,
                notification_type='app_status',
                title="Application Update",
                content=f"Your application for {application.job.title} has been updated to '{status_labels.get(status, status)}'.",
                link='/students/applications/'
            )
            
            # Log Activity for Student
            from My_Job_Portal.utils import log_activity as log_student_activity
            log_student_activity(
                application.student.user,
                "Application Status Updated",
                f"Your application for {application.job.title} is now {status_labels.get(status, status)}",
                "fa-solid fa-paper-plane"
            )
            
            # Email to Student
            send_email_notification(
                subject=f"Update on your application: {application.job.title}",
                template_name='emails/status_update.html',
                context={
                    'student_name': application.student.user.name or application.student.user.username,
                    'job_title': application.job.title,
                    'company_name': application.job.company,
                    'status': status_labels.get(status, status),
                    'dashboard_url': request.build_absolute_uri('/students/applications/')
                },
                recipient_list=[application.student.user.email]
            )
    else:
        messages.error(request, "Invalid status.")
    return redirect('manage_applications')


@login_required(login_url='recruiter_login')
@recruiter_required
def delete_application(request, app_id):
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    student_name = f"{application.first_name} {application.last_name}" if application.first_name else application.student.user.username if application.student else "Unknown"
    
    application.delete()
    
    log_activity(
        request.user,
        "Application Deleted",
        f"Discarded application from {student_name}",
        "fa-solid fa-trash-can"
    )
    
    messages.success(request, f"Application from {student_name} has been deleted.")
    return redirect('manage_applications')


@login_required(login_url='recruiter_login')
@recruiter_required
def schedule_interview(request, app_id):
    from Jobs.models import InterviewSchedule
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)

    if request.method == 'POST':
        scheduled_at = request.POST.get('scheduled_at')
        duration = request.POST.get('duration_minutes', 60)
        fmt = request.POST.get('format', 'video')
        location_or_link = request.POST.get('location_or_link', '')
        notes = request.POST.get('notes', '')

        interview, created = InterviewSchedule.objects.update_or_create(
            application=application,
            defaults={
                'scheduled_at': scheduled_at,
                'duration_minutes': duration,
                'format': fmt,
                'location_or_link': location_or_link,
                'notes': notes,
            }
        )

        # Update application status to 'interview'
        application.status = 'interview'
        application.save()

        # Notify student
        if application.student:
            from Accounts.models import Notification
            Notification.objects.create(
                user=application.student.user,
                notification_type='interview',
                title="Interview Scheduled! 🎉",
                content=f"Your interview for {application.job.title} has been scheduled.",
                link='/students/applications/'
            )
            send_email_notification(
                subject=f"Interview Scheduled for {application.job.title}",
                template_name='emails/interview_scheduled.html',
                context={
                    'student_name': application.student.user.name or application.student.user.username,
                    'job_title': application.job.title,
                    'company_name': application.job.company,
                    'scheduled_at': interview.scheduled_at,
                    'format': interview.get_format_display(),
                    'location_or_link': interview.location_or_link,
                    'notes': interview.notes,
                    'dashboard_url': request.build_absolute_uri('/students/applications/')
                },
                recipient_list=[application.student.user.email]
            )

        action = "scheduled" if created else "updated"
        messages.success(request, f"Interview {action} successfully!")
        return redirect('manage_applications')

    # GET: render a modal-compatible JSON or redirect
    return redirect('manage_applications')


@login_required(login_url='recruiter_login')
@recruiter_required
def cancel_interview(request, app_id):
    from Jobs.models import InterviewSchedule
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    InterviewSchedule.objects.filter(application=application).delete()
    application.status = 'shortlisted'
    application.save()
    messages.success(request, "Interview cancelled.")
    return redirect('manage_applications')


@login_required
def approval_pending(request):
    if request.user.role != 'recruiter':
        return redirect('home')
    if request.user.is_approved:
        return redirect('recruiter_dashboard')
    return render(request, 'recruiters/approval_pending.html')



@login_required(login_url='recruiter_login')
@recruiter_required
def recruiter_profile(request):
    from .models import Recruiter
    from .forms import RecruiterProfileForm
    from Jobs.models import Application

    recruiter, created = Recruiter.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.name or request.user.username}
    )

    if request.method == 'POST':
        form = RecruiterProfileForm(request.POST, request.FILES, instance=recruiter)
        if form.is_valid():
            form.save()
            log_activity(
                request.user,
                "Profile Updated",
                "Updated recruiter profile and company information",
                "fa-solid fa-building"
            )
            messages.success(request, "Profile updated successfully!")
            return redirect('recruiter_profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RecruiterProfileForm(instance=recruiter)

    # Public stats
    user_jobs = Job.objects.filter(recruiter=request.user)
    total_apps = Application.objects.filter(job__recruiter=request.user)

    context = {
        'form': form,
        'recruiter': recruiter,
        'total_jobs_posted': user_jobs.count(),
        'total_active_jobs': user_jobs.filter(is_active=True).count(),
        'total_hires': total_apps.filter(status='shortlisted').count(),
        'total_applications': total_apps.count(),
    }
    return render(request, 'recruiters/recruiter_profile.html', context)

@login_required(login_url='recruiter_login')
@recruiter_required
def analytics(request):
    # Mock data for charts
    context = {
        'views_per_job': [
            {'title': 'Senior Developer', 'views': 450, 'apps': 45},
            {'title': 'UI/UX Designer', 'views': 320, 'apps': 28},
            {'title': 'Marketing Lead', 'views': 180, 'apps': 12},
        ],
        'monthly_stats': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'views': [1200, 1900, 1700, 2100, 2400, 2800],
            'apps': [100, 150, 140, 180, 210, 250],
        },
        'conversion_rate': 8.5,
        'drop_off_rate': 12.2,
    }
    return render(request, 'recruiters/analytics.html', context)


@login_required(login_url='recruiter_login')
@recruiter_required
def manage_candidates(request):
    # Mock talent pool data
    candidates = [
        {'name': 'Alex Johnson', 'role': 'Senior Python Developer', 'match_score': 98, 'status': 'Shortlisted', 'avatar': 'https://ui-avatars.com/api/?name=Alex+Johnson&background=1e6f63&color=fff'},
        {'name': 'Sarah Williams', 'role': 'UI/UX Designer', 'match_score': 92, 'status': 'Under Review', 'avatar': 'https://ui-avatars.com/api/?name=Sarah+Williams&background=6366f1&color=fff'},
        {'name': 'Michael Chen', 'role': 'Fullstack Engineer', 'match_score': 85, 'status': 'New', 'avatar': 'https://ui-avatars.com/api/?name=Michael+Chen&background=f59e0b&color=fff'},
        {'name': 'Emily Davis', 'role': 'Marketing Manager', 'match_score': 78, 'status': 'New', 'avatar': 'https://ui-avatars.com/api/?name=Emily+Davis&background=ec4899&color=fff'},
    ]
    return render(request, 'recruiters/manage_candidates.html', {'candidates': candidates})


@login_required(login_url='recruiter_login')
@recruiter_required
def recruiter_settings(request):
    from .models import RecruiterSetting
    settings, created = RecruiterSetting.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'notifications':
            settings.email_notifications = 'email_notifications' in request.POST
            settings.new_application_alert = 'new_application_alert' in request.POST
            settings.shortlisted_candidate_alert = 'shortlisted_candidate_alert' in request.POST
            settings.payment_invoice_alert = 'payment_invoice_alert' in request.POST
            settings.weekly_report_email = 'weekly_report_email' in request.POST
            settings.marketing_emails = 'marketing_emails' in request.POST
            settings.save()
            messages.success(request, "Notification preferences updated.")

        elif action == 'job_defaults':
            settings.default_job_expiry_days = request.POST.get('expiry_days', 30)
            settings.allow_remote_default = 'allow_remote' in request.POST
            settings.default_location = request.POST.get('default_location', '')
            settings.default_salary_visibility = 'salary_visibility' in request.POST
            settings.save()
            messages.success(request, "Job posting defaults updated.")

        elif action == 'privacy':
            settings.show_profile_publicly = 'show_profile' in request.POST
            settings.show_name_publicly = 'show_name' in request.POST
            settings.allow_direct_messaging = 'allow_dm' in request.POST
            settings.allow_candidate_save_company = 'allow_save' in request.POST
            settings.save()
            messages.success(request, "Privacy settings updated.")
            
        elif action == 'account':
            # Password change logic would go here if using a form
            # For now, let's just show success for other account toggles
            request.user.two_factor_enabled = '2fa_enabled' in request.POST
            request.user.save()
            messages.success(request, "Account security settings updated.")

        return redirect('recruiter_settings')

    return render(request, 'recruiters/settings.html', {'settings': settings})


@login_required(login_url='recruiter_login')
@recruiter_required
def recruiter_billing(request):
    import razorpay
    from django.conf import settings as django_settings
    from .models import Subscription, Invoice

    subscription, _ = Subscription.objects.get_or_create(user=request.user)
    invoices = Invoice.objects.filter(user=request.user).order_by('-date')

    PLAN_PRICES = {'free': 0, 'pro': 4900, 'enterprise': 19900}  # amounts in paise (INR)

    razorpay_order = None
    selected_plan = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upgrade':
            new_plan = request.POST.get('plan')
            if new_plan in PLAN_PRICES and new_plan != 'free':
                client = razorpay.Client(
                    auth=(django_settings.RAZORPAY_KEY_ID, django_settings.RAZORPAY_KEY_SECRET)
                )
                order_data = {
                    'amount': PLAN_PRICES[new_plan],
                    'currency': 'INR',
                    'receipt': f'receipt_{request.user.id}_{new_plan}',
                    'notes': {
                        'user_id': str(request.user.id),
                        'plan': new_plan,
                    }
                }
                try:
                    razorpay_order = client.order.create(data=order_data)
                    selected_plan = new_plan
                except Exception as e:
                    messages.error(request, f"Payment gateway error: {e}")
                    return redirect('recruiter_billing')
            elif new_plan == 'free':
                subscription.plan = 'free'
                subscription.save()
                messages.success(request, "Switched to the Free plan.")
                return redirect('recruiter_billing')

        elif action == 'toggle_renewal':
            subscription.auto_renew = not subscription.auto_renew
            subscription.save()
            status = "enabled" if subscription.auto_renew else "disabled"
            messages.info(request, f"Auto-renewal has been {status}.")
            return redirect('recruiter_billing')

    return render(request, 'recruiters/billing.html', {
        'subscription': subscription,
        'invoices': invoices,
        'razorpay_order': razorpay_order,
        'selected_plan': selected_plan,
        'razorpay_key_id': django_settings.RAZORPAY_KEY_ID,
    })


@login_required(login_url='recruiter_login')
@recruiter_required
def razorpay_success(request):
    """Called via AJAX after successful Razorpay payment to record the invoice."""
    import razorpay, hmac, hashlib
    from django.conf import settings as django_settings
    from .models import Subscription, Invoice

    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        razorpay_order_id = data.get('razorpay_order_id', '')
        razorpay_payment_id = data.get('razorpay_payment_id', '')
        razorpay_signature = data.get('razorpay_signature', '')
        plan = data.get('plan', 'pro')

        # Verify signature
        key_secret = django_settings.RAZORPAY_KEY_SECRET.encode()
        msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
        generated_sig = hmac.new(key_secret, msg, hashlib.sha256).hexdigest()

        if generated_sig == razorpay_signature:
            PLAN_PRICES = {'pro': 49.00, 'enterprise': 199.00}
            subscription, _ = Subscription.objects.get_or_create(user=request.user)
            subscription.plan = plan
            subscription.save()

            Invoice.objects.create(
                user=request.user,
                invoice_number=f"INV-{razorpay_payment_id[:8].upper()}",
                amount=PLAN_PRICES.get(plan, 0),
                plan_name=plan.capitalize(),
                status='paid',
            )
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Signature mismatch'}, status=400)

    return JsonResponse({'status': 'error'}, status=405)



@login_required(login_url='recruiter_login')
@recruiter_required
def manage_team(request):
    from .models import TeamMember, Recruiter
    recruiter_profile = Recruiter.objects.get(user=request.user)
    team_members = TeamMember.objects.filter(company=recruiter_profile)

    if request.method == 'POST':
        action = request.POST.get('action')
        member_id = request.POST.get('member_id')
        
        if action == 'update_role':
            new_role = request.POST.get('role')
            member = TeamMember.objects.get(id=member_id, company=recruiter_profile)
            member.role = new_role
            member.save()
            messages.success(request, f"Updated {member.user.email}'s role to {new_role}.")
            
        elif action == 'remove':
            member = TeamMember.objects.get(id=member_id, company=recruiter_profile)
            email = member.user.email
            member.delete()
            messages.warning(request, f"Removed {email} from the team.")

        return redirect('manage_team')

    # Seed some mock data if empty for demonstration
    if not team_members.exists():
        # Ideally would use a service but for now let's just show what it looks like
        # We won't actually create them in DB unless we have real Users
        pass

    return render(request, 'recruiters/manage_team.html', {
        'team_members': team_members,
        'recruiter': recruiter_profile
    })


@login_required(login_url='recruiter_login')
@recruiter_required
def get_candidate_details(request, app_id):
    from django.http import JsonResponse
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    student = application.student
    
    # Live Skills
    live_skills = []
    if student:
        live_skills = list(student.skills.values_list('name', flat=True))

    data = {
        'id': application.id,
        'name': f"{application.first_name} {application.last_name}" if application.first_name else student.user.name or student.user.username if student else "Unknown",
        'email': application.email or (student.user.email if student else "N/A"),
        'phone': application.phone or (student.phone if student else "N/A"),
        'job_title': application.job.title,
        'applied_at': application.applied_at.strftime('%b %d, %Y'),
        'status': application.status,
        'cover_letter': application.cover_letter,
        'snapshot_skills': application.skills,
        'live_skills': live_skills,
        'bio': student.bio if student else "",
        'headline': student.headline if student else "",
        'github': student.github if student else "",
        'linkedin': student.linkedin if student else "",
        'portfolio': student.portfolio if student else "",
        'notes': application.notes,
        'resume_url': application.resume.url if application.resume else (student.resume.url if student and student.resume else None),
        'graduate': application.graduate,
        'salary_range': f"{application.min_salary} - {application.max_salary}"
    }
    return JsonResponse(data)


@login_required(login_url='recruiter_login')
@recruiter_required
def save_application_notes(request, app_id):
    if request.method == 'POST':
        from django.http import JsonResponse
        import json
        application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
        data = json.loads(request.body)
        application.notes = data.get('notes', '')
        application.save()
        return JsonResponse({'status': 'success'})
    from django.http import JsonResponse
    return JsonResponse({'status': 'error'}, status=400)


@login_required(login_url='recruiter_login')
@recruiter_required
def market_insights(request):
    from Jobs.models import Category, Job
    from django.db.models import Count, Avg
    import random

    # Real data from categories
    categories = Category.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')

    # Mock more detailed trends and benchmarks for the insights page
    insights_data = []
    colors = ['#1e6f63', '#6366f1', '#f59e0b', '#ec4899', '#8b5cf6', '#10b981']
    
    for i, cat in enumerate(categories[:6]):
        insights_data.append({
            'name': cat.name,
            'job_count': cat.job_count,
            'avg_salary': random.randint(5, 25), # LPA
            'demand_trend': random.randint(5, 20), # percentage
            'color': colors[i % len(colors)],
            'competition_level': random.choice(['High', 'Medium', 'Low'])
        })

    # Summary stats
    total_market_jobs = Job.objects.count()
    top_location = "Remote / Bangalore" # Mocking for now
    
    return render(request, 'recruiters/market_insights.html', {
        'insights': insights_data,
        'total_market_jobs': total_market_jobs,
        'top_location': top_location
    })
    

def public_company_profile(request, recruiter_id):
    from .models import Recruiter
    from Jobs.models import Job
    
    recruiter = get_object_or_404(Recruiter, id=recruiter_id)
    active_jobs = Job.objects.filter(recruiter=recruiter.user, is_active=True, is_approved=True).order_by('-created_at')
    
    return render(request, 'recruiters/public_company_profile.html', {
        'recruiter': recruiter,
        'active_jobs': active_jobs
    })
