from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'users/profile.html')

def organization_settings(request):
    return HttpResponse('Organization settings placeholder')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
