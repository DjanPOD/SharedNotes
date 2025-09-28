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

from django.urls import path, include
from doc import views

app_name = 'doc'

urlpatterns = [
    # These url patterns are commented out because the corresponding views.py
    # has not been implemented yet. Please both the url Name and views are subject to change based on need
    # and whether they are function or class based views (see above)
    #path('', views.doc_view, name='doc'),
    path('upload/', views.upload_document, name='upload_document'),
    path('<int:document_id>/', views.document_detail, name='document_detail'),
    path('<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('<int:document_id>/like/', views.like_document, name='like_document'),
    path('<int:document_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('search/', views.search_documents, name='search_documents'),
    # path('<int:doc_id>', views.DocView.as_view, name='doc'),
]