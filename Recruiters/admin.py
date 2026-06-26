from django.contrib import admin
from .models import Recruiter

class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'company_website')
    list_filter = ('company_name',)
    search_fields = ('user__name', 'user__email', 'company_name')

admin.site.register(Recruiter, RecruiterAdmin)
