from django import forms
from django.contrib.auth.forms import UserCreationForm
from Accounts.models import User


class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user



class RecruiterRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True)
    company_website = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ['name', 'email', 'username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'recruiter'
        if commit:
            user.save()
            from Recruiters.models import Recruiter
            Recruiter.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name'),
                company_website=self.cleaned_data.get('company_website', '')
            )
        return user



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'profile_picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-l', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control-l', 'placeholder': 'Email Address'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-l', 'onchange': 'previewImage(this)'}),
        }
