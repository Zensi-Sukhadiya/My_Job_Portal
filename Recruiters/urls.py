from django.urls import path
from . import views

urlpatterns = [
    path('recruiter_dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('manage-jobs/', views.manage_jobs, name='manage_jobs'),
    path('manage-applications/', views.manage_applications, name='manage_applications'),
    path('update-status/<int:app_id>/<str:status>/', views.update_application_status, name='update_application_status'),
    path('approval-pending/', views.approval_pending, name='approval_pending'),
    path('profile/', views.recruiter_profile, name='recruiter_profile'),
    path('analytics/', views.analytics, name='recruiter_analytics'),
    path('candidates/', views.manage_candidates, name='manage_candidates'),
    path('settings/', views.recruiter_settings, name='recruiter_settings'),
    path('billing/', views.recruiter_billing, name='recruiter_billing'),
    path('team/', views.manage_team, name='manage_team'),
    path('candidate-details/<int:app_id>/', views.get_candidate_details, name='get_candidate_details'),
    path('application-notes/<int:app_id>/', views.save_application_notes, name='save_application_notes'),
    path('market-insights/', views.market_insights, name='market_insights'),
    path('company/<int:recruiter_id>/', views.public_company_profile, name='public_company_profile'),
    path('schedule-interview/<int:app_id>/', views.schedule_interview, name='schedule_interview'),
    path('cancel-interview/<int:app_id>/', views.cancel_interview, name='cancel_interview'),
    path('delete-application/<int:app_id>/', views.delete_application, name='delete_application'),
    path('billing/razorpay-success/', views.razorpay_success, name='razorpay_success'),
]
