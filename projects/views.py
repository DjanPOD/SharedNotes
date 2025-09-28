import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Project, JoinRequest
from profiles.models import Profile
from .forms import ProjectForm
from .models import ProjectComment
from .forms import ProjectCommentForm
from classes.models import Class


def is_pma_admin(user):
    if not user.is_authenticated:
        return False
    try:
        profile = Profile.objects.get(user=user)
        return profile.user_type == "PMA Admin"
    except Profile.DoesNotExist:
        return False

@login_required
def project_list(request, *args, **kwargs):
    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
            
    if is_pma_admin(request.user):
        return redirect('projects:pma_admin_dashboard')  
    else:
        # No class_id provided; retrieve all projects the user is a member of
        class_instance = None
        owned_projects = Project.objects.filter(owner=request.user)
        member_projects = Project.objects.filter(members=request.user).exclude(owner=request.user)

        return render(request, 'projects/project_list.html', {
            'class': class_instance,
            'owned_projects': owned_projects,
            'member_projects': member_projects,
        })

def pma_admin_dashboard(request, *args, **kwargs):
    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    

    class_instance = Class.objects.get(pma_admins__id=request.user.id)       
    if not is_pma_admin(request.user):
        messages.error(request, "Please go to My Projects Dashboard.")
        return redirect('project_list')
    
    else:
        projects = class_instance.project_set.all()
        return render(request, 'projects/pma_projects.html', {'projects': projects, 'class': class_instance})

@login_required
def add_project(request, class_id):
    class_instance = get_object_or_404(Class, class_id=class_id)

    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    if is_pma_admin(request.user):
        messages.error(request, "PMA Admin is not allowed to Add Project.")
        return redirect('classes:class_detail', class_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.class_belongs_to  = class_instance
            project.folder_in_s3 = f"documents/project-{uuid.uuid4()}"
            project.save()
            project.members.add(request.user)
            messages.success(request, "Project created successfully!")
            return redirect('classes:class_detail', class_id=class_id)
    else:
        form = ProjectForm()
    return render(request, 'projects/add_project.html', {'form': form, 'class': class_instance})


@login_required
def project_view(request, class_id, project_id):   
    class_instance = get_object_or_404(Class, class_id=class_id)
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)

    documents = project.document_set.all()
    comments = project.comments.all()  # Get all comments
    comment_form = ProjectCommentForm()

    if request.method == 'POST':
        comment_form = ProjectCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.project = project
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect('classes:projects:project_detail', class_id=class_id, project_id=project_id)


    join_requests = JoinRequest.objects.filter(project=project,
                                               approved=False) if request.user == project.owner else None
    
    return render(request, 'projects/project_detail.html', {
        'class': class_instance,
        'project': project,
        'documents': documents,
        'comments': comments,
        'comment_form': comment_form,
        'join_requests': join_requests,
    })

@login_required
def add_member(request, class_id, project_id):
    class_instance = get_object_or_404(Class, class_id=class_id)

    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    if is_pma_admin(request.user):
        messages.error(request, "PMA Admin is not allowed to Add Member.")
        return redirect('classes:projects:project_detail', class_id, project_id)
    
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
    
    if request.user != project.owner:
        messages.error(request, "Only the project owner can add members.")
        return redirect('projects:project_detail', class_id=class_id, project_id=project_id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if user in project.members.all():
                messages.error(request, f"{username} is already a member of the project.")
            else:
                project.members.add(user)
                messages.success(request, f"{username} has been added to the project.")
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
    return redirect('classes:projects:project_detail', class_id=class_id, project_id=project_id)

@login_required
def remove_member(request, class_id, project_id, user_id):
    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')

    # Fetch the project and user
    project = get_object_or_404(Project, project_id=project_id)
    user_to_remove = get_object_or_404(User, id=user_id)

    # Check if the current user is the project owner
    if request.user == project.owner:
        if user_to_remove in project.members.all():
            project.members.remove(user_to_remove)
            messages.success(request, f"{user_to_remove.username} has been removed from the project.")
        else:
            messages.error(request, f"{user_to_remove.username} is not a member of this project.")
    else:
        messages.error(request, "You are not authorized to remove members from this project.")

    return redirect('classes:projects:project_detail', class_id=class_id, project_id=project_id)

@login_required
def request_to_join_project(request, class_id, project_id):
    class_instance = get_object_or_404(Class, class_id=class_id)

    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    if is_pma_admin(request.user):
        messages.error(request, "PMA Admin is not allowed to Join Project.")
        return redirect('classes:projects:project_detail', class_id, project_id)
    
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)

    if request.method == 'POST':
        if request.user in project.members.all():
            messages.error(request, "You are already a member of this project.")
        else:
            # Check if a join request already exists
            join_request, created = JoinRequest.objects.get_or_create(user=request.user, project=project)
            if created:
                messages.success(request, "Your request to join the project has been sent.")
                # Optionally notify the project owner
                # You could use signals, email, or other messaging here
            else:
                messages.info(request, "You have already requested to join this project.")

    return redirect('classes:projects:project_detail', class_id=class_id, project_id=project_id)

@login_required
def approve_request(request, class_id, project_id, user_id):
    class_instance = get_object_or_404(Class, class_id=class_id)

    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    if is_pma_admin(request.user):
        messages.error(request, "PMA Admin is not allowed to Approve Join Request.")
        return redirect('classes:projects:project_detail', class_id, project_id)
    
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
    user = get_object_or_404(User, id=user_id)

    if request.user == project.owner:
        project.members.add(user)
        JoinRequest.objects.filter(project=project, user=user).delete()  # Assuming you have a JoinRequest model
        messages.success(request, f"{user.username} has been added to the project.")
        messages.add_message(request, messages.INFO, f"Your request to join '{project.name}' was approved!",
                             extra_tags="user_notification")

    return redirect('classes:projects:project_detail', class_id=class_id, project_id=project_id)


@login_required
def deny_request(request, class_id, project_id, user_id):
    class_instance = get_object_or_404(Class, class_id=class_id)

    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    if is_pma_admin(request.user):
        messages.error(request, "PMA Admin is not allowed to Deny Join Request.")
        return redirect('classes:projects:project_detail', class_id, project_id)
    
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
    user = get_object_or_404(User, id=user_id)

    if request.user == project.owner:
        JoinRequest.objects.filter(project=project, user=user).delete()  # Assuming you have a JoinRequest model
        messages.info(request, f"{user.username}'s join request has been denied.")
        messages.add_message(request, messages.WARNING, f"Your request to join '{project.name}' was denied.",
                             extra_tags="user_notification")

    return redirect('classes:projects:project_detail', class_id=class_id, project_id=project_id)

@login_required
def delete_project(request, class_id, project_id):
    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    
    class_instance = get_object_or_404(Class, class_id=class_id)
    project = get_object_or_404(Project, project_id=project_id, class_belongs_to=class_instance)
  
    if request.user == project.owner or is_pma_admin(request.user):
        project.delete(user=request.user)
        messages.success(request, "Project deleted successfully.")
        return redirect('classes:class_detail', class_id=class_id)
    else:
        messages.error(request, "You are not allowed to delete this project.")
        return redirect('projects:project_detail', class_id=class_id, project_id=project.project_id)

@login_required
def delete_comment(request,class_id, project_id, comment_id):
    project = Project.objects.get(project_id=project_id)

    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')
    if is_pma_admin(request.user):
        messages.error(request, "PMA Admin is not allowed to Delete Join Comment.")
        return redirect('classes:projects:project_detail', project.class_belongs_to.class_id, project_id)
    
    comment = get_object_or_404(ProjectComment, id=comment_id, project__project_id=project_id)
    
    # Only allow comment author or project owner to delete comments
    if request.user == comment.author or request.user == comment.project.owner:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this comment.")
    
    return redirect('classes:projects:project_detail', class_id=class_id, project_id=project_id)

@login_required
def leave_project(request, project_id):
    if request.user.username == 'guest':
        messages.error(request, "Access restricted for Anonymous Users.")
        return redirect('home')

    if request.method == "POST":
        # Retrieve the project
        project = get_object_or_404(Project, project_id=project_id)

        # Check if the user is a member
        if request.user in project.members.all():
            project.members.remove(request.user)
            messages.success(request, "You have successfully left the project.")
        else:
            messages.error(request, "You are not a member of this project.")

        return redirect('projects:project_list')  # Update to your correct URL name

        # Redirect if accessed without POST
    messages.error(request, "Invalid request.")
    return redirect('projects:project_list')
