from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('student_login/', views.student_login, name='student_login'),
    path('student_register/', views.student_register, name='student_register'),
    path('recruiter_login/', views.recruiter_login, name='recruiter_login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/recruiter_login.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
