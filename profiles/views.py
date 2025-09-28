from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Profile
from django.contrib.auth.models import User
from .forms import ProfileForm
    
@login_required
def profile_view(request, username):
    if request.user.username == 'guest':
        messages.warning(request, "Access restricted.")
        return redirect('home')
    
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'profiles/profile.html', {'profile': profile})

@login_required
def edit_profile_view(request, username):
    user = get_object_or_404(User, username=username)

    if user != request.user:
        return redirect('profiles:profile', username)

    profile = request.user.profile

    exclude_admin_fields = profile.user_type == 'PMA Admin'

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, exclude_admin_fields=exclude_admin_fields)
        if form.is_valid():
            form.save()
            return redirect('profiles:profile', username)

    else:
        form = ProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }, exclude_admin_fields=exclude_admin_fields)

    return render(request, 'profiles/editprofile.html', {'form': form})


