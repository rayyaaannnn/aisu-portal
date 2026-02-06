from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Profile
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt


def role_required(role_name):
    """
    Decorator that checks if the logged-in user has the required role.
    Returns JSON response for API requests.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            try:
                profile = Profile.objects.get(user=request.user)
                if profile.role != role_name:
                    return JsonResponse(
                        {'error': f"Access denied. You must have the '{role_name}' role."},
                        status=403
                    )
            except Profile.DoesNotExist:
                return JsonResponse({'error': 'Access denied. No profile found.'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
@require_http_methods(["GET"])
def dashboard_counts(request):
    """Return dashboard statistics as JSON."""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    # Get counts based on user role
    total_users = User.objects.count()
    total_states = Profile.objects.exclude(state__isnull=True).exclude(state__exact='').values('state').distinct().count()
    total_districts = Profile.objects.exclude(district__isnull=True).exclude(district__exact='').values('district').distinct().count()
    
    user_role = profile.role
    
    data = {
        'total_users': total_users,
        'total_states': total_states,
        'total_districts': total_districts,
        'user_role': user_role,
    }
    return JsonResponse(data)


@login_required
@require_http_methods(["GET"])
def my_profile(request):
    """Get current user's profile as JSON."""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': profile.role,
        'state': profile.state,
        'district': profile.district,
        'phone': profile.phone,
        'photo_url': profile.photo_url,
    }
    return JsonResponse(data)


@login_required
@require_http_methods(["PUT"])
def update_profile(request):
    """Update current user's profile."""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user = request.user
    
    # Update user fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        user.email = data['email']
    user.save()
    
    # Update profile fields
    if 'state' in data:
        profile.state = data['state']
    if 'district' in data:
        profile.district = data['district']
    if 'phone' in data:
        profile.phone = data['phone']
    if 'photo_url' in data:
        profile.photo_url = data['photo_url']
    profile.save()
    
    return JsonResponse({'message': 'Profile updated successfully'})


@login_required
@require_http_methods(["GET"])
def manage_users(request):
    """List all users (super_admin only)."""
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'super_admin':
            return JsonResponse({'error': 'Access denied. Super admin only.'}, status=403)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    users = User.objects.all().prefetch_related('profile')
    users_data = []
    for user in users:
        try:
            user_profile = user.profile
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user_profile.role,
                'state': user_profile.state,
                'district': user_profile.district,
            })
        except Profile.DoesNotExist:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': None,
                'state': None,
                'district': None,
            })
    
    return JsonResponse({'users': users_data})


@login_required
@require_http_methods(["POST"])
def add_user(request):
    """Create a new user (super_admin only)."""
    import json
    
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'super_admin':
            return JsonResponse({'error': 'Access denied. Super admin only.'}, status=403)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    if not all([username, email, password, role]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)
    
    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    # Create profile
    Profile.objects.create(
        user=user,
        role=role,
        state=data.get('state'),
        district=data.get('district'),
    )
    
    return JsonResponse({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role,
        }
    })


@login_required
@require_http_methods(["PUT"])
def edit_user(request, user_id):
    """Edit an existing user (super_admin only)."""
    import json
    
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'super_admin':
            return JsonResponse({'error': 'Access denied. Super admin only.'}, status=403)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    try:
        user_profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(user=user, role='district_team')
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Update user fields
    if 'email' in data:
        user.email = data['email']
    user.save()
    
    # Update profile fields
    if 'role' in data:
        user_profile.role = data['role']
    if 'state' in data:
        user_profile.state = data['state']
    if 'district' in data:
        user_profile.district = data['district']
    user_profile.save()
    
    return JsonResponse({'message': 'User updated successfully'})


@login_required
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """Delete a user (super_admin only)."""
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'super_admin':
            return JsonResponse({'error': 'Access denied. Super admin only.'}, status=403)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Prevent deleting yourself
    if user == request.user:
        return JsonResponse({'error': 'You cannot delete your own account'}, status=400)
    
    user.delete()
    return JsonResponse({'message': 'User deleted successfully'})


@require_http_methods(["POST"])
def api_login(request):
    """API login - returns user info for React frontend."""
    import json
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return JsonResponse({'error': 'Username and password required'}, status=400)
    
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    
    login(request, user)
    
    try:
        profile = Profile.objects.get(user=user)
        role = profile.role
    except Profile.DoesNotExist:
        role = 'unknown'
    
    return JsonResponse({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role,
        }
    })


@login_required
@require_http_methods(["POST"])
def api_logout(request):
    """API logout."""
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})


@login_required
@require_http_methods(["GET"])
def role_redirect(request):
    """Return role-based redirect info."""
    try:
        profile = Profile.objects.get(user=request.user)
        role = profile.role
    except Profile.DoesNotExist:
        role = 'unknown'
    
    return JsonResponse({
        'role': role,
        'redirect_url': f'/{role.replace("_", "-")}'
    })

