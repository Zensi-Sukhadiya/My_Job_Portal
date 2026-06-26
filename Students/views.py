from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Jobs.models import Application
from My_Job_Portal.utils import log_activity, render_to_pdf
from django.http import HttpResponse
from Jobs.models import Job, SavedJob

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    # Get or create student profile
    from .models import Student
    student_profile, created = Student.objects.get_or_create(user=request.user)
    
    # Analytics
    from Jobs.models import Application, Job, SavedJob
    total_applications = Application.objects.filter(student=student_profile)
    
    apps_count = total_applications.count()
    pending_count = total_applications.filter(status='pending').count()
    shortlisted_count = total_applications.filter(status='shortlisted').count()
    rejected_count = total_applications.filter(status='rejected').count()
    saved_jobs_count = SavedJob.objects.filter(student=student_profile).count()
    
    # Recent Activity
    activities = request.user.activities.all().order_by('-timestamp')[:8]
    
    # Recommended Jobs (Based on skills or just recent jobs for now)
    recommended_jobs = Job.objects.filter(is_active=True, is_approved=True).order_by('-created_at')[:4]
    
    # Recent Applications
    recent_apps = total_applications.select_related('job').order_by('-applied_at')[:5]
    
    # Saved Job IDs for icons
    saved_job_ids = SavedJob.objects.filter(student=student_profile).values_list('job_id', flat=True)
    
    context = {
        'student': student_profile,
        'apps_count': apps_count,
        'pending_count': pending_count,
        'shortlisted_count': shortlisted_count,
        'rejected_count': rejected_count,
        'saved_jobs_count': saved_jobs_count,
        'profile_completion': request.user.profile_completion,
        'activities': activities,
        'recommended_jobs': recommended_jobs,
        'recent_apps': recent_apps,
        'saved_job_ids': saved_job_ids,
    }
    return render(request, 'students/student_dashboard.html', context)

from .forms import StudentProfileForm, EducationForm, ExperienceForm, ProjectForm, CertificationForm, LanguageForm, SkillForm
from .models import Student, Education, Experience, Project, Certification, Language, Skill

@login_required
def edit_profile(request):
    student, created = Student.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            # Log Activity
            from My_Job_Portal.utils import log_activity
            log_activity(request.user, "Profile Updated", "Updated professional summary and details", "fa-solid fa-user-pen")
            messages.success(request, "Profile updated successfully!")
            return redirect('edit_profile')
    else:
        form = StudentProfileForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
        'education_list': student.education.all(),
        'experience_list': student.experience.all(),
        'projects_list': student.projects.all(),
        'certifications_list': student.certifications.all(),
        'languages_list': student.languages.all(),
        'skills_list': student.skills.all(),
    }
    return render(request, 'students/edit_profile.html', context)

@login_required
def my_applications(request):
    from Jobs.models import Application
    student = request.user.student_profile
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')
    
    applications = Application.objects.filter(student=student).select_related('job').order_by('-applied_at')
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    if query:
        applications = applications.filter(job__title__icontains=query)
    
    context = {
        'applications': applications,
        'active_tab': 'applications',
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'students/my_applications.html', context)

@login_required
def saved_jobs(request):
    """View to list all saved jobs for the student."""
    student = request.user.student_profile
    saved_jobs = SavedJob.objects.filter(student=student).select_related('job').order_by('-saved_at')
    
    context = {
        'saved_jobs': saved_jobs,
        'active_tab': 'saved_jobs',
    }
    return render(request, 'students/saved_jobs.html', context)

@login_required
def save_job(request, job_id):
    """View to toggle saving/bookmarking a job without messages."""
    student = request.user.student_profile
    job = get_object_or_404(Job, id=job_id)

    saved_job = SavedJob.objects.filter(student=student, job=job)
    
    if saved_job.exists():
        saved_job.delete()
    else:
        SavedJob.objects.create(student=student, job=job)

    # Redirect back to previous page or dashboard
    return redirect(request.META.get('HTTP_REFERER', 'student_dashboard'))

@login_required
def withdraw_application(request, app_id):
    from Jobs.models import Application
    application = get_object_or_404(Application, id=app_id, student__user=request.user)
    if application.status == 'pending':
        application.delete()
        messages.success(request, "Application withdrawn successfully. You can now re-apply with any corrections.")
    else:
        messages.error(request, "You cannot withdraw an application that is already being processed.")
    return redirect('my_applications')

@login_required
def delete_application(request, app_id):
    from Jobs.models import Application
    application = get_object_or_404(Application, id=app_id, student__user=request.user)
    application.delete()
    messages.success(request, "Application has been removed from your history.")
    return redirect('my_applications')

@login_required
def add_education(request):
    if request.method == 'POST':
        student = request.user.student_profile
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.student = student
            edu.save()
            messages.success(request, "Education record added!")
        else:
            messages.error(request, "Failed to add education. Check your inputs.")
    return redirect('edit_profile')

@login_required
def add_experience(request):
    if request.method == 'POST':
        student = request.user.student_profile
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.student = student
            exp.save()
            messages.success(request, "Experience record added!")
        else:
            messages.error(request, "Failed to add experience.")
    return redirect('edit_profile')

@login_required
def add_skill(request):
    if request.method == 'POST':
        student = request.user.student_profile
        skill_name = request.POST.get('skill_name')
        if skill_name:
            Skill.objects.get_or_create(student=student, name=skill_name)
            messages.success(request, f"Skill '{skill_name}' added!")
    return redirect('edit_profile')

@login_required
def add_project(request):
    if request.method == 'POST':
        student = request.user.student_profile
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.student = student
            project.save()
            messages.success(request, "Project added successfully!")
        else:
            messages.error(request, "Failed to add project.")
    return redirect('edit_profile')

@login_required
def add_certification(request):
    if request.method == 'POST':
        student = request.user.student_profile
        form = CertificationForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.student = student
            cert.save()
            messages.success(request, "Certification added successfully!")
        else:
            messages.error(request, "Failed to add certification.")
    return redirect('edit_profile')

@login_required
def add_language(request):
    if request.method == 'POST':
        student = request.user.student_profile
        form = LanguageForm(request.POST)
        if form.is_valid():
            lang = form.save(commit=False)
            lang.student = student
            lang.save()
            messages.success(request, "Language added successfully!")
        else:
            messages.error(request, "Failed to add language.")
    return redirect('edit_profile')

@login_required
def notifications_list(request):
    notifications = request.user.notifications.all().order_by('-timestamp')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'active_tab': 'notifications',
    }
    return render(request, 'students/notifications.html', context)

@login_required
def mark_notification_read(request, notif_id):
    from Accounts.models import Notification
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications_list')

@login_required
def messages_list(request):
    from Accounts.models import Message
    from django.db.models import Q
    from django.contrib.auth.models import User
    # Get unique contacts
    messages_received = request.user.received_messages.all()
    messages_sent = request.user.sent_messages.all()
    
    # Get unique users involved in conversations
    contact_ids = set()
    for m in messages_received: contact_ids.add(m.sender_id)
    for m in messages_sent: contact_ids.add(m.recipient_id)
    
    contacts = User.objects.filter(id__in=contact_ids)
    
    selected_user_id = request.GET.get('user')
    selected_user = None
    chat_messages = []
    
    if selected_user_id:
        selected_user = get_object_or_404(User, id=selected_user_id)
        chat_messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=selected_user)) |
            (Q(sender=selected_user) & Q(recipient=request.user))
        ).order_by('timestamp')
        # Mark as read
        chat_messages.filter(recipient=request.user, is_read=False).update(is_read=True)
        
    context = {
        'contacts': contacts,
        'selected_user': selected_user,
        'chat_messages': chat_messages,
        'active_tab': 'messages',
    }
    return render(request, 'students/messages.html', context)

@login_required
def send_message(request):
    if request.method == 'POST':
        from Accounts.models import Message
        recipient_id = request.POST.get('recipient_id')
        body = request.POST.get('body')
        if recipient_id and body:
            recipient = get_object_or_404(User, id=recipient_id)
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                body=body
            )
            return redirect(f"/students/messages/?user={recipient_id}")
    return redirect('messages_list')

@login_required
def student_settings(request):
    if request.method == 'POST':
        from django.contrib.auth import update_session_auth_hash
        from django.contrib.auth.forms import PasswordChangeForm
        
        action = request.POST.get('action')
        if action == 'password':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully!')
                return redirect('student_settings')
            else:
                messages.error(request, 'Please correct the error below.')
        
        elif action == 'privacy':
            student = request.user.student_profile
            student.is_public = 'is_public' in request.POST
            student.save()
            messages.success(request, 'Privacy settings updated.')
            return redirect('student_settings')

    from django.contrib.auth.forms import PasswordChangeForm
    context = {
        'password_form': PasswordChangeForm(request.user),
        'active_tab': 'settings',
    }
    return render(request, 'students/settings.html', context)

@login_required
def delete_record(request, model_type, record_id):
    student = request.user.student_profile
    model_map = {
        'education': Education,
        'experience': Experience,
        'project': Project,
        'certification': Certification,
        'skill': Skill,
        'language': Language,
        'saved_job': SavedJob,
    }
    
    if model_type in model_map:
        model = model_map[model_type]
        record = get_object_or_404(model, id=record_id, student=student)
        record.delete()
        messages.success(request, f"{model_type.capitalize()} deleted.")
    
    if model_type == 'saved_job':
        return redirect('saved_jobs')
    return redirect('edit_profile')

@login_required
def download_resume(request):
    student = get_object_or_404(Student, user=request.user)
    
    context = {
        'student': student,
        'education_list': student.education.all(),
        'experience_list': student.experience.all(),
        'projects_list': student.projects.all(),
        'certifications_list': student.certifications.all(),
        'languages_list': student.languages.all(),
        'skills_list': student.skills.all(),
    }
    
    pdf = render_to_pdf('students/resume_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"{student.user.name or student.user.username}_Resume.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Error generating PDF", status=400)
