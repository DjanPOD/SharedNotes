"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
#COOMMENTTT
from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'login'
urlpatterns = [
    #These url patterns are commented out because the corresponding views.py
    # has not been implemented yet. Please both the url Name and views are subject to change based on need
    # and whether they are function or class based views (see above)

    # path('', views.login, name='login'),
    # path('register/', views.register, name='register'),

    path('', views.log_in, name='login'),
    path('anonymous/', views.anonymous_login, name='anonymous_login'),

    path('logout/', views.log_out, name='logout'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path('user-info/', views.user_info, name='user_info'),
    path('pma-info/', views.pma_info, name='pma_info'),

]


