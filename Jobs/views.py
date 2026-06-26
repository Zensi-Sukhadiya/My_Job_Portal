from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from .models import Job, Application, Category, SavedJob
from Students.models import Student
from Accounts.models import User
from My_Job_Portal.utils import log_activity, send_email_notification


def home(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')

    jobs = Job.objects.filter(is_approved=True).order_by('-created_at')
    
    if category_slug:
        jobs = jobs.filter(category__slug=category_slug)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if query:
        jobs = jobs.filter(title__icontains=query)
    
    categories = Category.objects.annotate(job_count=Count('jobs')).order_by('-job_count')[:5]
    
    # Trust Signals Data
    total_jobs_count = Job.objects.filter(is_approved=True).count()
    total_companies_count = User.objects.filter(role='recruiter').count()
    total_candidates_count = User.objects.filter(role='student').count()

    # Saved Job IDs for icons if student
    saved_job_ids = []
    if request.user.is_authenticated and request.user.role == 'student':
        try:
            student = request.user.student_profile
            saved_job_ids = SavedJob.objects.filter(student=student).values_list('job_id', flat=True)
        except:
            pass

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('jobs/partials/job_list_partial.html', {'jobs': jobs, 'saved_job_ids': saved_job_ids}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'jobs/index.html', {
        'jobs': jobs[:6], # Show only latest 6 on home page
        'categories': categories,
        'selected_category': category_slug,
        'selected_location': location,
        'selected_job_type': job_type,
        'query': query,
        'total_jobs_count': total_jobs_count,
        'total_companies_count': total_companies_count,
        'total_candidates_count': total_candidates_count,
        'saved_job_ids': saved_job_ids,
    })



def job_listings(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')

    jobs = Job.objects.filter(is_approved=True).order_by('-created_at')
    
    if category_slug:
        jobs = jobs.filter(category__slug=category_slug)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if query:
        jobs = jobs.filter(title__icontains=query)
    
    # Pagination
    paginator = Paginator(jobs, 9) # 9 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.annotate(job_count=Count('jobs')).order_by('-job_count')
    
    # Saved Job IDs for icons if student
    saved_job_ids = []
    if request.user.is_authenticated and request.user.role == 'student':
        try:
            student = request.user.student_profile
            saved_job_ids = SavedJob.objects.filter(student=student).values_list('job_id', flat=True)
        except:
            pass

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('jobs/partials/job_list_partial.html', {'jobs': page_obj, 'saved_job_ids': saved_job_ids}, request=request)
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'page_number': page_obj.number
        })
        
    return render(request, 'jobs/job_listings.html', {
        'jobs': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'selected_location': location,
        'selected_job_type': job_type,
        'query': query,
        'job_types': Job.JOB_TYPE_CHOICES,
        'saved_job_ids': saved_job_ids,
    })



def job_details(request, id):
    job = get_object_or_404(Job, id=id)
    job.views += 1
    job.save()

    jobs = Job.objects.filter(category=job.category).exclude(id=job.id)[:6]
    categories = Category.objects.annotate(job_count=Count('jobs')).order_by('-job_count')

    # AI Skills Match Score
    skills_match_score = None
    matched_skills = []
    missing_skills = []
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        student_skills = [s.name.lower() for s in student.skills.all()]
        # Build a searchable corpus from the job
        job_corpus = (job.title + ' ' + job.description).lower()
        for skill in student_skills:
            if skill in job_corpus:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
        if student_skills:
            skills_match_score = int((len(matched_skills) / len(student_skills)) * 100)

    # Company Reviews
    from .models import CompanyReview
    company_reviews = CompanyReview.objects.filter(
        company_recruiter=job.recruiter
    ).order_by('-created_at')
    avg_rating = None
    if company_reviews.exists():
        from django.db.models import Avg
        avg_rating = company_reviews.aggregate(Avg('rating'))['rating__avg']

    # Has current student already reviewed?
    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = company_reviews.filter(reviewer=request.user).exists()

    # Is job saved?
    is_saved = False
    has_applied = False
    if request.user.is_authenticated and request.user.role == 'student':
        try:
            student = request.user.student_profile
            is_saved = SavedJob.objects.filter(student=student, job=job).exists()
            has_applied = Application.objects.filter(student=student, job=job).exists()
        except:
            pass

    return render(request, 'jobs/job_details.html', {
        'job': job,
        'jobs': jobs,
        'categories': categories,
        'skills_match_score': skills_match_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'company_reviews': company_reviews,
        'avg_rating': avg_rating,
        'user_reviewed': user_reviewed,
        'is_saved': is_saved,
        'has_applied': has_applied,
    })


from .forms import JobForm, ApplicationForm
from django.http import JsonResponse

@login_required(login_url='recruiter_login')
def improve_description(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        desc = data.get('description', '')
        
        # Mock AI Improvement Logic
        professional_intro = "We are seeking a highly motivated and detail-oriented professional to join our dynamic team. "
        professional_outro = "\n\nKey Requirements:\n- Proven experience in the relevant field\n- Strong communication and problem-solving skills\n- Ability to work effectively in a team environment"
        
        improved_desc = professional_intro + desc + professional_outro
        
        return JsonResponse({'improved_description': improved_desc})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='student_login')
def job_apply(request, job_id):
    if request.user.role == 'recruiter':
        messages.error(request, "Recruiters cannot apply for jobs. Please use a student account.")
        return redirect('job_details', id=job_id)

    job = get_object_or_404(Job, id=job_id)
    if request.method == "POST":
        
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect('home')

        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = student
            application.job = job
            application.save()
            
            # Log for Student
            log_activity(request.user, "Applied for Job", f"Applied to {job.title} at {job.company}", "fa-solid fa-paper-plane")
            
            # Email to Recruiter
            recruiter_user = job.recruiter
            recruiter_profile = getattr(recruiter_user, 'recruiter', None)
            send_email_notification(
                subject=f"New Application for {job.title}",
                template_name='emails/new_application.html',
                context={
                    'recruiter_name': recruiter_profile.company_name if recruiter_profile else recruiter_user.name or recruiter_user.username,
                    'job_title': job.title,
                    'candidate_name': f"{application.first_name} {application.last_name}" if application.first_name else request.user.name or request.user.username,
                    'candidate_email': application.email or request.user.email,
                    'dashboard_url': request.build_absolute_uri('/recruiters/applications/')
                },
                recipient_list=[recruiter_user.email]
            )
            
            messages.success(request, "Application submitted successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
            return render(request, 'jobs/job_apply.html', {'job': job, 'categories': Category.objects.all(), 'form': form})
            
    return render(request, 'jobs/job_apply.html', {'job': job, 'categories': Category.objects.all()})



def job_details_general(request):
    jobs = Job.objects.order_by('-created_at')[:6]
    total_jobs = Job.objects.count()
    categories = Category.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')

    default_description = """
    Welcome to JobPortal – your gateway to exciting career opportunities.

    Explore the latest job openings across multiple industries including IT,
    Finance, Marketing, Design, and more. Each listing provides detailed
    information about responsibilities, qualifications, and application
    deadlines to help you make informed decisions.

    Whether you're a fresh graduate or an experienced professional,
    we connect talented candidates with top companies looking for
    the right skills and passion.

    Start exploring and take the next step in your career today.
    """

    return render(request, 'jobs/job_details.html', {
        'job': None,
        'jobs': jobs,
        'categories': categories,
        'default_description': default_description,
        'total_jobs': total_jobs,
    })



@login_required
def post_job(request):
    if request.user.role != 'recruiter':
        messages.error(request, "Only recruiters can post jobs.")
        return redirect('home')

    if request.method == "POST":
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            # In a real SaaS, maybe auto-approve or wait for admin
            job.is_approved = True 
            job.save()
            log_activity(request.user, "Job Posted", f"Published new job: {job.title}", "fa-solid fa-briefcase")
            messages.success(request, "Job posted successfully!")
            return redirect('manage_jobs')
    else:
        form = JobForm()

    from .models import Category
    from django.db.models import Count
    import random

    # All categories for the dropdown
    categories = Category.objects.all()

    # Market insights: Top 3 categories with job counts and random trend
    market_insights = Category.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')[:3]

    # Add a random trend percentage for visual polish 
    for insight in market_insights:
        insight.trend = random.randint(5, 15)

    return render(request, 'jobs/post_job.html', {
        'form': form, 
        'categories': categories,
        'market_insights': market_insights
    })



@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if job.recruiter != request.user:
        messages.error(request, "You are not authorized to edit this job.")
        return redirect('manage_jobs')

    if request.method == "POST":
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('manage_jobs')
    else:
        form = JobForm(instance=job)

    from .models import Category
    from django.db.models import Count
    import random

    # All categories for the dropdown
    categories = Category.objects.all()

    # Market insights: Top 3 categories with job counts and random trend
    market_insights = Category.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')[:3]

    # Add a random trend percentage for visual polish 
    for insight in market_insights:
        insight.trend = random.randint(5, 15)

    return render(request, 'jobs/edit_job.html', {
        'form': form, 
        'job': job,
        'categories': categories,
        'market_insights': market_insights
    })



@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if job.recruiter != request.user:
        messages.error(request, "You are not authorized to delete this job.")
        return redirect('manage_jobs')
    
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('manage_jobs')

    return render(request, 'jobs/confirm_delete.html', {'job': job})

    
def market_insights_public(request):
    from django.db.models import Count
    import random
    
    categories = Category.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')

    # Aggregating some stats for the public view
    total_listings = Job.objects.count()
    
    insights = []
    # Mocking some trends and growth % for public consumption
    for cat in categories[:8]:
        insights.append({
            'name': cat.name,
            'count': cat.job_count,
            'growth': random.randint(10, 45),
            'demand': random.choice(['High', 'Growing', 'Stable']),
            'icon': cat.icon_class or 'fa-solid fa-briefcase'
        })

    return render(request, 'jobs/market_insights.html', {
        'insights': insights,
        'total_listings': total_listings
    })


@login_required
def submit_company_review(request, recruiter_id):
    from .models import CompanyReview
    from Accounts.models import User
    recruiter = get_object_or_404(User, id=recruiter_id, role='recruiter')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title', '').strip()
        pros = request.POST.get('pros', '').strip()
        cons = request.POST.get('cons', '').strip()
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        next_url = request.POST.get('next', '/')

        if not rating or not title:
            messages.error(request, "Rating and title are required.")
            return redirect(next_url)

        CompanyReview.objects.update_or_create(
            company_recruiter=recruiter,
            reviewer=request.user,
            defaults={
                'rating': int(rating),
                'title': title,
                'pros': pros,
                'cons': cons,
                'is_anonymous': is_anonymous,
            }
        )
        messages.success(request, "Your review has been submitted. Thank you!")
        return redirect(next_url)

    return redirect('home')
