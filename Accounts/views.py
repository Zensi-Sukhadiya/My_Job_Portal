from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm, RecruiterRegistrationForm, UserProfileForm
from Students.models import Student
from Recruiters.models import Recruiter



from My_Job_Portal.utils import log_activity

def student_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            log_activity(user, "Logged In", "Signed in to student account", "fa-solid fa-right-to-bracket")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password")
    return render(request, 'accounts/student_login.html')

def student_register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.save()
            Student.objects.create(user=user)
            log_activity(user, "Account Created", "Registered as a new student", "fa-solid fa-user-plus")
            messages.success(request, "Registration successful! You can now login.")
            return redirect('student_login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/student_register.html', {'form': form})


def recruiter_login(request):
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == 'login':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.role == 'recruiter':
                    login(request, user)
                    log_activity(user, "Logged In", "Signed in to recruiter dashboard", "fa-solid fa-right-to-bracket")
                    if not user.is_approved:
                        return redirect('approval_pending')
                    return redirect('recruiter_dashboard')
                else:
                    messages.error(request, "Access denied. Not a recruiter account.")
            else:
                messages.error(request, "Invalid email or password.")
        elif form_type == 'register':
            pass1 = request.POST.get('password1')
            pass2 = request.POST.get('password2')
            if pass1 != pass2:
                messages.error(request, "Passwords do not match.")
            else:
                form = RecruiterRegistrationForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    log_activity(user, "Account Created", "Registered as a new recruiter", "fa-solid fa-user-plus")
                    messages.success(request, "Registration successful! Await admin approval.")
                    return redirect('recruiter_login')
                else:
                    for error in form.errors.values():
                        messages.error(request, error)
    return render(request, 'accounts/recruiter_login.html')


def logout(request):
    if request.user.is_authenticated:
        log_activity(request.user, "Logged Out", "Signed out of the platform", "fa-solid fa-right-from-bracket")
    auth_logout(request)
    return redirect('home')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Profile Updated", "Updated personal details", "fa-solid fa-user-pen")
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Fetch recent security/account activity
    recent_activity = request.user.activities.all().order_by('-timestamp')[:5]
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'recent_activity': recent_activity
    })
