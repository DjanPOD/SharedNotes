from django.shortcuts import render

# Create your views here.
import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from profiles.models import Profile
from django.contrib import messages


from mysite.views import home


@csrf_exempt
def log_in(request):

    if os.getenv('DYNO') is None:
        # Localhost (development)
        login_uri = f'http://localhost:8000/login/auth-receiver'
    else:
        # Running on Heroku, use the Heroku domain
        login_uri = f'https://swe-project-1323c34b4211.herokuapp.com/login/auth-receiver'
    context = {
        'google_client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'login_uri':login_uri
    }
    print(context)

    return render(request, 'login/login.html', context)


@csrf_exempt
def user_info(request):
    """
    Displays the user information for non-superusers.
    """
    # Get user data from the session
    user_data = request.session.get('user_data')

    if not user_data:
        return HttpResponse("No user data found.", status=403)
    
    return render(request, 'login/user-info.html', {'user_data': user_data})

@csrf_exempt
def pma_info(request):
    """
    Displays the user information for non-superusers.
    """
    # Get user data from the session
    user_data = request.session.get('user_data')

    if not user_data:
        return HttpResponse("No user data found.", status=403)
    
    return render(request, 'login/pma-info.html', {'user_data': user_data})



@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    print('Inside')
    token = request.POST.get('credential')

    if not token:
        print("No token received")
        return HttpResponse(status=403, content="Missing or invalid token")

    try:
        # Verify the Google token and get user info
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
        email = user_data['email'].lower() # Normalize email address (convert to lowercase)
        first_name = user_data.get('given_name', '')
        last_name = user_data.get('family_name', '')
    except ValueError:
        print("Token verification failed")
        return HttpResponse(status=403)

    first_time_user = False
    
    # Check if the user already exists in Django's User model
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # If user does not exist, create a new user
        user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name)
        Profile.objects.get_or_create(user=user)
        user.set_unusable_password()  # Set unusable password since they log in with Google
        user.save()
        first_time_user = True

    # Log the user in
    user.backend = 'django.contrib.auth.backends.ModelBackend'  # Set the backend explicitly
    login(request, user)

    request.session['user_data'] = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    }
    
    if(first_time_user):
        return redirect('profiles:editprofile', user.username)
    
    return redirect('/myprojects')


"""
    Signs out the user from both Django and Google accounts.
"""
def log_out(request):
    # Log out the user from Django
    logout(request)
    # Clear session data
    request.session.flush()

    # Redirect to Google logout URL
    return redirect(home)

def anonymous_login(request):
    if not request.user.is_authenticated:
        guest_password = os.getenv('GUEST_PASSWORD')  # Ensure this is defined in your environment
        guest_user, created = User.objects.get_or_create(username='guest')
        
        if created:  # Optionally set a password or perform other actions for new users
            guest_user.set_password(guest_password)  # If you want to set a password
            guest_user.save()

        login(request, guest_user, backend='django.contrib.auth.backends.ModelBackend')  # Specify the backend
        messages.success(request, "Logged in as Guest.")
        return redirect('classes:class_list')

    else:
        messages.info(request, "You are already logged in.")
        return redirect('classes:class_list')