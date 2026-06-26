from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('job_listings/', views.job_listings, name='job_listings'),
    path('job_details/', views.job_details_general, name='job_details_general'),
    path('job/<int:id>/', views.job_details, name='job_details'),
    path('apply/<int:job_id>/', views.job_apply, name='job_apply'),
    path('post_job/', views.post_job, name='post_job'),
    path('edit_job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('market-insights/', views.market_insights_public, name='market_insights_public'),
    path('improve-description/', views.improve_description, name='improve_description'),
    path('review/<int:recruiter_id>/', views.submit_company_review, name='submit_company_review'),
]
