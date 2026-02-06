from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from .models import Profile
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt


def role_required(role_name):
    """
    Decorator that checks if the logged-in user has the required role.
    
    Args:
        role_name (str): The required role (e.g., 'super_admin', 'it_team', 
                        'state_team', 'district_team')
    
    Returns:
        HttpResponseForbidden: If user doesn't have the required role
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                profile = Profile.objects.get(user=request.user)
                if profile.role != role_name:
                    return HttpResponseForbidden(
                        f"Access denied. You must have the '{role_name}' role to access this page."
                    )
            except Profile.DoesNotExist:
                return HttpResponseForbidden(
                    "Access denied. No profile found for this user."
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


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


@login_required
def dashboard_counts(request):
    # Return simple counts used by dashboards
    total_users = User.objects.count()
    total_states = Profile.objects.exclude(state__isnull=True).exclude(state__exact='').values('state').distinct().count()
    total_districts = Profile.objects.exclude(district__isnull=True).exclude(district__exact='').values('district').distinct().count()

    data = {
        'total_users': total_users,
        'total_states': total_states,
        'total_districts': total_districts,
    }
    return JsonResponse(data)


@login_required
def profile_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # create a basic profile if missing
        profile = Profile.objects.create(user=request.user, role='district_team')

    message = None
    if request.method == 'POST':
        # update user fields
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        # update profile fields
        state = request.POST.get('state') or None
        district = request.POST.get('district') or None
        phone = request.POST.get('phone', '').strip() or None
        photo_url = request.POST.get('photo_url', '').strip() or None

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        profile.state = state
        profile.district = district
        profile.phone = phone
        profile.photo_url = photo_url
        profile.save()

        message = 'Profile updated successfully.'

    context = {
        'profile': profile,
        'message': message,
    }
    return render(request, 'accounts/profile.html', context)

@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('role_redirect')
        else:
            error = 'Invalid username or password'
            return render(request, 'accounts/login.html', {'error': error})
    
    context = {}
    return render(request, 'accounts/login.html', context)


@login_required
def role_redirect(request):
    try:
        profile = Profile.objects.get(user=request.user)

        if profile.role == 'super_admin':
            return redirect('super_admin')
        elif profile.role == 'it_team':
            return redirect('it_dashboard')
        elif profile.role == 'state_team':
            return redirect('state_dashboard')
        elif profile.role == 'district_team':
            return redirect('district_dashboard')
    except Profile.DoesNotExist:
        return redirect('login')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def manage_users(request):
    # Only super admins can manage users
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'super_admin':
            return redirect('role_redirect')
    except Profile.DoesNotExist:
        return redirect('login')
    
    users = User.objects.all().prefetch_related('profile')
    context = {'users': users}
    return render(request, 'accounts/manage_users.html', context)


@login_required
def add_user(request):
    # Only super admins can add users
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'super_admin':
            return redirect('role_redirect')
    except Profile.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if User.objects.filter(username=username).exists():
            context = {'error': 'Username already exists'}
            return render(request, 'accounts/add_user.html', context)
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create profile
        Profile.objects.create(user=user, role=role)
        
        return redirect('manage_users')
    
    context = {}
    return render(request, 'accounts/add_user.html', context)


@login_required
def edit_user(request, user_id):
    # Only super admins can edit users
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'super_admin':
            return redirect('role_redirect')
    except Profile.DoesNotExist:
        return redirect('login')
    
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(Profile, user=user)
    
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user_profile.role = request.POST.get('role')
        user_profile.state = request.POST.get('state') or None
        user_profile.district = request.POST.get('district') or None
        
        user.save()
        user_profile.save()
        
        return redirect('manage_users')
    
    context = {'user': user, 'profile': user_profile}
    return render(request, 'accounts/edit_user.html', context)


@login_required
def delete_user(request, user_id):
    # Only super admins can delete users
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'super_admin':
            return redirect('role_redirect')
    except Profile.DoesNotExist:
        return redirect('login')
    
    user = get_object_or_404(User, id=user_id)
    # prevent super-admin from deleting themselves
    if user == request.user:
        context = {'user': user, 'error': 'You cannot delete your own account.'}
        return render(request, 'accounts/confirm_delete.html', context)

    if request.method == 'POST':
        user.delete()
        return redirect('manage_users')

    context = {'user': user}
    return render(request, 'accounts/confirm_delete.html', context)
