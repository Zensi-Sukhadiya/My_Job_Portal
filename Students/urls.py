from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.edit_profile, name='edit_profile'),
    path('applications/', views.my_applications, name='my_applications'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('save-job/<int:job_id>/', views.save_job, name='save_job'),
    path('withdraw/<int:app_id>/', views.withdraw_application, name='withdraw_application'),
    path('delete-application/<int:app_id>/', views.delete_application, name='delete_application'),
    
    # Professional Records CRUD
    path('add-education/', views.add_education, name='add_education'),
    path('add-experience/', views.add_experience, name='add_experience'),
    path('add-project/', views.add_project, name='add_project'),
    path('add-certification/', views.add_certification, name='add_certification'),
    path('add-language/', views.add_language, name='add_language'),
    path('add-skill/', views.add_skill, name='add_skill'),
    path('delete-record/<str:model_type>/<int:record_id>/', views.delete_record, name='delete_record'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # Messages
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/send/', views.send_message, name='send_message'),
    
    # Settings
    path('settings/', views.student_settings, name='student_settings'),
    
    # Resume PDF
    path('download-resume/', views.download_resume, name='download_resume'),
]
