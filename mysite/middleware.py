from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class SuperuserRedirectMiddleware:
    """
    Middleware to restrict superusers to only the admin page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the user is authenticated and a superuser, but not accessing the admin page
        if request.user.is_authenticated and request.user.is_superuser:
            admin_url = reverse('admin:index')  # Admin index page URL
            # Check if the user is trying to access a non-admin page
            if not request.path.startswith(reverse('admin:index')):
                return redirect(admin_url)

        response = self.get_response(request)
        return response
