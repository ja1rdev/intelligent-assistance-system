"""
URL configuration for face_auth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from os import name
from django.contrib import admin
from django.urls import path
from accounts import views
from face_auth import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('', views.face, name='face'),
    path('users/', views.users, name='users'),
    path('user/delete/<int:pk>/', views.delete, name='delete'),
    path('attendance/remove/<int:pk>/', views.remove, name='remove'),
    path('user/update/<int:pk>/', views.update, name='update'),
    path('signup/', views.signup, name='signup'),
    path('main/', views.main, name='main'),
    path('logout/', views.signout, name='logout'),
    path('face/', views.face, name='face'),
]