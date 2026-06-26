from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter so that when a user logs in with Google,
    we set their role to 'student' and ensure a Student profile exists.
    """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Set default role to student if not already set
        if not user.role:
            user.role = 'student'
            user.save()

        # Auto-create student profile
        if user.role == 'student':
            from Students.models import Student
            Student.objects.get_or_create(user=user)

        return user

    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated:
            if user.role == 'recruiter':
                return '/recruiters/recruiter_dashboard/'
            return '/students/student_dashboard/'
        return settings.LOGIN_REDIRECT_URL
