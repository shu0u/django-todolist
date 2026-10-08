"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path, include
from todo.views import (
    home, delete_task, toggle_task, edit_task, 
    api_task_list, api_task_detail, signup,
    completed_tasks,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('delete/<int:task_id>/', delete_task, name='delete_task'),
    path('toggle/<int:task_id>/', toggle_task, name='toggle_task'),
    path('edit/<int:task_id>/', edit_task, name='edit_task'),

    path('api/v1/tasks/', api_task_list, name='api_task_list'),
    path('api/v1/tasks/<int:pk>/', api_task_detail, name='api_task_detail'),

    path('completed/', completed_tasks, name='completed_tasks'),
    path('accounts/signup/', signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
]