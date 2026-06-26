from django.shortcuts import redirect
from django.contrib import messages

def recruiter_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'recruiter':
            messages.error(request, "Access denied.")
            return redirect('home')

        if not request.user.is_approved:
            messages.warning(request, "Your account is pending approval.")
            return redirect('approval_pending')

        return view_func(request, *args, **kwargs)
    return wrapper
