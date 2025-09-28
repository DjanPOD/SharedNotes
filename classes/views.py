from django.shortcuts import render, get_object_or_404
from .models import Class
from django.contrib.auth.decorators import login_required

def class_list(request):
    classes = Class.objects.all()
    return render(request, 'classes/all_classes.html', {'classes': classes})

@login_required
def class_detail(request, class_id):
    class_instance = get_object_or_404(Class, class_id=class_id)
    projects = class_instance.project_set.all()
    context = {
        'class': class_instance,
        'projects': projects,
    }
    return render(request, 'classes/class.html', context)