from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
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


def _rate_limit(key_prefix, limit=5, window=300):
    """Simple in-memory/IP-based rate limit using cache."""
    key = f"rl:{key_prefix}"
    current = cache.get(key, 0)
    if current >= limit:
        return False
    cache.incr(key, 1) if cache.get(key) else cache.set(key, 1, timeout=window)
    return True


@csrf_exempt
@require_http_methods(["POST"])
def password_reset_request(request):
    """Start password reset. Returns uid and token (dev) and should email in production."""
    import json
    if not _rate_limit(f"pwreset:{request.META.get('REMOTE_ADDR')}", limit=5, window=900):
        return JsonResponse({'error': 'Too many attempts. Please wait and try again.'}, status=429)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    identifier = data.get('identifier')
    if not identifier:
        return JsonResponse({'error': 'Username or email required'}, status=400)

    try:
        user = User.objects.get(username=identifier)
    except User.DoesNotExist:
        user = User.objects.filter(email=identifier).first()

    if not user:
        # Do not reveal whether account exists
        return JsonResponse({'message': 'If an account exists, a reset link has been sent.'})

    token_gen = PasswordResetTokenGenerator()
    token = token_gen.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Send email (console backend in dev)
    reset_link = f"{getattr(settings, 'FRONTEND_RESET_URL', 'http://localhost:3000/forgot')}?uid={uid}&token={token}"
    send_mail(
        subject="AISU password reset",
        message=f"Use this link to reset your password: {reset_link}",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@aisu.local'),
        recipient_list=[user.email] if user.email else [],
        fail_silently=True,
    )

    return JsonResponse({'message': 'If an account exists, a reset link has been sent.'})


@csrf_exempt
@require_http_methods(["POST"])
def password_reset_confirm(request):
    """Complete password reset using uid + token + new_password."""
    import json
    if not _rate_limit(f"pwreset-confirm:{request.META.get('REMOTE_ADDR')}", limit=10, window=900):
        return JsonResponse({'error': 'Too many attempts. Please wait and try again.'}, status=429)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    uidb64 = data.get('uid')
    token = data.get('token')
    new_password = data.get('new_password')

    if not all([uidb64, token, new_password]):
        return JsonResponse({'error': 'uid, token and new_password are required'}, status=400)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return JsonResponse({'error': 'Invalid reset link'}, status=400)

    token_gen = PasswordResetTokenGenerator()
    if not token_gen.check_token(user, token):
        return JsonResponse({'error': 'Invalid or expired token'}, status=400)

    user.set_password(new_password)
    user.save()
    return JsonResponse({'message': 'Password has been reset successfully'})


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
