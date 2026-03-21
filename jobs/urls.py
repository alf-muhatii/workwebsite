"""
URL configuration for jobsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from jobs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
path('post/', views.post_job, name='post_job'),
path('register/', views.register_view, name='register'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('delete/<int:job_id>/', views.delete_job, name='delete_job'),
path('save/<int:job_id>/', views.save_job, name='save_job'),
path('saved/', views.saved_jobs, name='saved_jobs'),
path('profile/', views.profile, name='profile'),
path('edit-profile/', views.edit_profile, name='edit_profile'),
path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),

]


