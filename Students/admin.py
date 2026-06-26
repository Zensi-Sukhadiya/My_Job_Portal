from django.contrib import admin
from .models import Student, Education, Experience, Project, Certification, Language, Skill

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'phone', 'headline')
    search_fields = ('user__username', 'user__email', 'college', 'headline')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('student', 'institution', 'degree', 'start_date', 'is_currently_studying')
    list_filter = ('is_currently_studying',)

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'role', 'start_date', 'is_current')
    list_filter = ('is_current',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'start_date')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'issuing_organization', 'issue_date')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'proficiency')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('student', 'name')
    search_fields = ('name',)
