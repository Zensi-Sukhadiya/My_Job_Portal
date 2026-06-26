from django import forms
from .models import Job, Application


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'category', 'job_type', 'salary', 'description', 'logo', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'job-desc'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control-l'}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'first_name', 'last_name', 'email', 'phone', 
            'min_salary', 'max_salary', 'graduate', 'skills', 
            'resume', 'cover_letter'
        ]
