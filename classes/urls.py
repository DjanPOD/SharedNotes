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

from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'classes'
urlpatterns = [
    # These url patterns are commented out because the corresponding views.py
    # has not been implemented yet. Please both the url Name and views are subject to change based on need
    # and whether they are function or class based views (see above)

    # path("", views.ClassView.as_view(), name="class"),
    # path("doc/", include("docs.urls"))
    path('', views.class_list, name='class_list'),
    path('<int:class_id>/', views.class_detail, name='class_detail'),
    path('<int:class_id>/projects/', include('projects.urls', namespace='projects')),
]