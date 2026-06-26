from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='platform_admin_dashboard'),
    path('jobs/', views.manage_jobs, name='admin_manage_jobs'),
    path('job/approve/<int:job_id>/', views.approve_job, name='approve_job'),
    path('job/reject/<int:job_id>/', views.reject_job, name='reject_job'),
    path('recruiters/', views.manage_recruiters, name='admin_manage_recruiters'),
    path('recruiter/approve/<int:user_id>/', views.approve_recruiter, name='approve_recruiter'),
    path('users/', views.manage_users, name='admin_manage_users'),
    path('user/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('applications/', views.view_all_applications, name='admin_view_all_applications'),
    path('analytics/', views.admin_analytics, name='admin_analytics'),
]
