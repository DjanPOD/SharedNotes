from django.shortcuts import render


def home(request):
    return render(request,'home.html')

def project_list(request):
    return render(request, 'project_list.html')