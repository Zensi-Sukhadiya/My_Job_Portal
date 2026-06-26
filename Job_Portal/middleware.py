# yourapp/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class RecruiterApprovalMiddleware(MiddlewareMixin):

    def process_request(self, request):

        # If user is not logged in → do nothing
        if not request.user.is_authenticated:
            return None

        # If user is recruiter and NOT approved
        if request.user.role == "recruiter" and not request.user.is_approved:

            # Allowed URLs while pending
            allowed_paths = [
                reverse('approval_pending'),
                reverse('logout'),
            ]

            # If trying to access any other page
            if request.path not in allowed_paths:
                return redirect('approval_pending')

        return None
