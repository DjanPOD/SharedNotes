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
from doc import views as doc_views

app_name = 'projects'
urlpatterns = [
    # These url patterns are commented out because the corresponding views.py
    # has not been implemented yet. Please both the url Name and views are subject to change based on need
    # and whether they are function or class based views (see above)

    path('search/', doc_views.search_documents, name='search_documents'),  # Add this line first
    path("add/", views.add_project, name="add_project"),
    path("<int:project_id>/doc/", include("doc.urls")),
    # path('<int:class_id>/', views.project_list, name='project_list'),
    path('', views.project_list, name='project_list'),
    path('add/', views.add_project, name='add_project_without_class'),

    path('<int:project_id>/add_member/', views.add_member, name='add_member'),
    path('<int:project_id>/', views.project_view, name='project_detail'),
    path('<int:project_id>/delete/', views.delete_project, name='delete_project'), 
    path('<int:class_id>/<int:project_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    path('pma_admin_dashboard/', views.pma_admin_dashboard, name='pma_admin_dashboard'),

    path('project/<int:project_id>/request_to_join/', views.request_to_join_project, name='request_to_join_project'),
    path('project/<int:project_id>/approve_request/<int:user_id>/', views.approve_request, name='approve_request'),
    path('project/<int:project_id>/deny_request/<int:user_id>/', views.deny_request, name='deny_request'),
    path('projects/<int:project_id>/leave/', views.leave_project, name='leave_project'),
    path('projects/<int:project_id>/remove_member/<int:user_id>/', views.remove_member, name='remove_member')


]



