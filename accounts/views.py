from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import Profile


@login_required
def super_admin_dashboard(request):
    return render(request, 'accounts/super_admin.html')

@login_required
def it_dashboard(request):
    return render(request, 'accounts/it_dashboard.html')

@login_required
def state_dashboard(request):
    return render(request, 'accounts/state_dashboard.html')

@login_required
def district_dashboard(request):
    return render(request, 'accounts/district_dashboard.html')

def role_redirect(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role == 'super_admin':
        return redirect('super_admin')
    elif profile.role == 'it_team':
        return redirect('it_dashboard')
    elif profile.role == 'state_team':
        return redirect('state_dashboard')
    elif profile.role == 'district_team':
        return redirect('district_dashboard')
