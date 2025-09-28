import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Document, Like, DocumentComment, Tag
from django.contrib import messages
from projects.models import Project
from .forms import DocumentForm, DocumentCommentForm
from django.conf import settings
import boto3
from classes.models import Class


def is_pma_admin(user):
    return user.groups.filter(name='PMA Admin').exists()

@login_required
def upload_document(request, class_id, project_id):
    class_instance = get_object_or_404(Class, class_id=class_id)
    # Get the project associated with the project_id
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.project = project
            document.save()
            # Handle tags
            tags_input = form.cleaned_data.get('tags_input', '')
            if tags_input:
                tag_names = [t.strip().lower() for t in tags_input.split(',') if t.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    document.tags.add(tag)
            return redirect('classes:projects:doc:document_detail', class_id=class_id, project_id=project_id, document_id=document.id)
    else:
        form = DocumentForm()
        return render(request, 'doc/upload_document.html', {'form': form, 'project': project})

@login_required
def document_detail(request, class_id, project_id, document_id):
    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
      
    class_instance = get_object_or_404(Class, class_id=class_id)
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
    document = get_object_or_404(Document, id=document_id, project=project)

     # Create a set of viewed documents in the session if it doesn't exist
    if 'viewed_documents' not in request.session:
        request.session['viewed_documents'] = []
    
    # Check if this document has been viewed in this session
    viewed_documents = request.session['viewed_documents']
    if document_id not in viewed_documents:
        document.views += 1
        document.save()
        # Add the document ID to the viewed list
        viewed_documents.append(document_id)
        request.session['viewed_documents'] = viewed_documents
        request.session.modified = True

    file_extension = os.path.splitext(document.file.name)[1].lower()
    comments = document.comments.all()
    comment_form = DocumentCommentForm()

    # Determine if the file is a previewable type
    can_preview = file_extension in ['.pdf', '.png', '.jpg', '.jpeg', '.txt']

    if 'viewed_documents' not in request.session:
        request.session['viewed_documents'] = []

    # Handle new comment
    if request.method == 'POST':
        comment_form = DocumentCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.document = document
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect('classes:projects:doc:document_detail', class_id=class_id, project_id=project_id, document_id=document.id)

    # Split tags into a list
    tags = [tag.name for tag in document.tags.all()]

    is_liked_by_user = document.is_liked_by(request.user)

    context = {
        'class': class_instance,
        'project': project,
        'document': document,
        'comments': comments,
        'comment_form': comment_form,
        'tags': tags,
        'file_extension': file_extension,
        'can_preview': can_preview,
        'is_liked_by_user': is_liked_by_user,
    }
    return render(request, 'doc/document_detail.html', context)


@login_required
def delete_comment(request, class_id, project_id, document_id, comment_id):
    class_instance = get_object_or_404(Class, class_id=class_id)
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
    comment = get_object_or_404(DocumentComment, id=comment_id, document_id=document_id)
    
    # Only allow comment author, document owner, or project owner to delete comments
    if (request.user == comment.author or 
        request.user == comment.document.owner or 
        request.user == comment.document.project.owner):
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this comment.")
    
    return redirect('classes:projects:doc:document_detail', 
                   class_id=class_id,
                   project_id=project_id, 
                   document_id=document_id)

@login_required
def like_document(request, class_id, project_id, document_id):
    class_instance = get_object_or_404(Class, class_id=class_id)
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
    document = get_object_or_404(Document, id=document_id, project=project)

    was_liked = document.toggle_like(user=request.user)
        
    if was_liked:
        messages.success(request, "Document liked successfully!")
    else:
        messages.success(request, "Document unliked successfully!")

    return redirect('classes:projects:doc:document_detail', class_id=class_id, project_id=project_id, document_id=document.id)

@login_required
def delete_document(request, class_id, project_id, document_id):
    class_instance = get_object_or_404(Class, class_id=class_id)
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
    document = get_object_or_404(Document, id=document_id, project=project)

    # Check if the user is the owner or part of PMA admins
    if request.user == document.owner or request.user in document.project.get_all_pma_admins():
        try:
            document.delete(user=request.user)
            messages.success(request, "Document deleted successfully.")
            return redirect('classes:projects:project_detail', 
                          class_id=class_id, 
                          project_id=project_id)
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the document: {e}")
    else:
        messages.error(request, "You are not allowed to delete this document.")
    
    return redirect('classes:projects:doc:document_detail', 
                   class_id=class_id, 
                   project_id=project_id, 
                   document_id=document_id)

from django.db.models import Q

@login_required  
def search_documents(request):
    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    
    query = request.GET.get('q', '')
    if query:
        # First, get all projects the user has access to
        accessible_projects = Project.objects.filter(
            Q(owner=request.user) |  # Projects owned by user
            Q(members=request.user)   # Projects where user is a member
        ).distinct()

        # Then search for documents within those projects
        documents = Document.objects.filter(
            # Filter documents by accessible projects
            project__in=accessible_projects
        ).filter(
            # Apply search criteria
            Q(title__icontains=query) |  # Search in titles
            Q(tags__name__icontains=query)  # Search in tags
        ).distinct().select_related('project', 'owner').prefetch_related('tags')
        
        # Filter out documents with no project (if any exist)
        documents = [doc for doc in documents if doc.project and doc.project.project_id]
    else:
        documents = []
    
    context = {
        'documents': documents,
        'query': query,
    }
    return render(request, 'doc/search_results.html', context)
