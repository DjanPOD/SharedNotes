from django.utils.deprecation import MiddlewareMixin
from .models import Project

class EnsureOwnerInMembersMiddleware(MiddlewareMixin):
    """
    Middleware to ensure that the owner of a project is included in the project's members.
    """

    def process_request(self, request):
        # Only proceed if the user is authenticated
        if request.user.is_authenticated:
            # Fetch all projects owned by the current user
            owned_projects = Project.objects.filter(owner=request.user)

            for project in owned_projects:
                # Check if the owner is not in the members list
                if not project.members.filter(id=request.user.id).exists():
                    self.members.add(self.owner)
                    project.save()  # Save the project to persist the change, this directly calls add owner as member

        return None
