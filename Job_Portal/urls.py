from django.urls import path, include

urlpatterns = [
    path('', include('Jobs.urls')),
    path('auth/', include('Accounts.urls')),
    path('recruiters/', include('Recruiters.urls')),
    path('students/', include('Students.urls')),
    path('platform-admin/', include('Platform_Admin.urls')),
]
