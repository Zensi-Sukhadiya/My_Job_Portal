from django import forms
from .models import Recruiter


class RecruiterProfileForm(forms.ModelForm):

    class Meta:
        model = Recruiter
        fields = [
            # Basic Info
            'job_title', 'company_name', 'company_website', 'industry',
            'company_size', 'founded_year', 'company_description',
            # Contact
            'official_email', 'phone_number', 'address', 'city', 'state', 'country',
            'linkedin_profile', 'company_linkedin', 'twitter', 'facebook',
            # Branding
            'company_logo', 'cover_banner', 'company_video',
            # Verification
            'company_reg_number', 'gst_tax_id',
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={'placeholder': 'e.g. HR Manager, Talent Acquisition Lead'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Your company name'}),
            'company_website': forms.URLInput(attrs={'placeholder': 'https://yourcompany.com'}),
            'industry': forms.TextInput(attrs={'placeholder': 'e.g. Technology, Finance, Healthcare'}),
            'founded_year': forms.NumberInput(attrs={'placeholder': 'e.g. 2010', 'min': 1800, 'max': 2030}),
            'company_description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe your company culture, mission, and values...'}),
            'official_email': forms.EmailInput(attrs={'placeholder': 'hr@yourcompany.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+91 98765 43210'}),
            'address': forms.TextInput(attrs={'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State / Province'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'linkedin_profile': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'company_linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/company/yourcompany'}),
            'twitter': forms.URLInput(attrs={'placeholder': 'https://twitter.com/yourhandle'}),
            'facebook': forms.URLField.widget if False else forms.URLInput(attrs={'placeholder': 'https://facebook.com/yourpage'}),
            'company_video': forms.URLInput(attrs={'placeholder': 'YouTube or Vimeo URL'}),
            'company_reg_number': forms.TextInput(attrs={'placeholder': 'Company Registration Number'}),
            'gst_tax_id': forms.TextInput(attrs={'placeholder': 'GST / Tax Identification Number'}),
        }
