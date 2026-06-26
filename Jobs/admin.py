from django.contrib import admin
from .models import Job, Application, Category


class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'job_type', 'salary', 'recruiter', 'created_at')
    list_filter = ('category', 'job_type', 'created_at')
    search_fields = ('title', 'company', 'location', 'description')
    ordering = ('-created_at',)



class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__user__name', 'job__title', 'cover_letter')
    ordering = ('-applied_at',)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_class')



admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
