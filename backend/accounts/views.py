from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail, get_connection
from django.core.cache import cache
from django.conf import settings
from .models import Profile
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.utils import timezone
from functools import wraps
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


def jwt_login_required(view_func):
    """Custom decorator to handle both session and JWT authentication"""
    def wrapper(request, *args, **kwargs):
        # First try Django's session authentication
        if hasattr(request, 'user') and request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        # Then try JWT authentication
        jwt_auth = JWTAuthentication()
        try:
            # Authenticate returns (user, validated_token) or (None, None)
            user_token_tuple = jwt_auth.authenticate(request)
            if user_token_tuple is not None:
                request.user = user_token_tuple[0]  # Set user on request
                return view_func(request, *args, **kwargs)
        except AuthenticationFailed:
            pass

        # If neither worked, return unauthorized
        return JsonResponse({'error': 'Authentication credentials were not provided.'}, status=401)

    return wrapper


def require_roles(*roles):
    """
    Decorator to enforce role-based access on function-based views.
    Usage: @login_required @require_roles('super_admin', 'it_team')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            try:
                profile = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                return JsonResponse({'error': 'Profile not found'}, status=403)

            if roles and profile.role not in roles:
                return JsonResponse({'error': 'Access denied'}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


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


@jwt_login_required
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


@jwt_login_required
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


@csrf_exempt
@jwt_login_required
@require_http_methods(["PUT"])
def update_profile(request):
    """Update current user's profile."""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)

    user = request.user

    # Determine the type of data and handle accordingly
    if request.content_type and ('multipart/form-data' in request.content_type or 'application/x-www-form-urlencoded' in request.content_type):
        # Handle form data (multipart or urlencoded)
        data = request.POST

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
        # Handle photo_url field in form data (when no file is uploaded but URL is provided)
        if 'photo_url' in data:
            profile.photo_url = data['photo_url']

        # Handle file upload
        if 'photo' in request.FILES:
            photo_file = request.FILES['photo']

            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if photo_file.content_type not in allowed_types:
                return JsonResponse({'error': 'Invalid file type. Please upload an image (JPEG, PNG, GIF, or WebP).'}, status=400)

            # Validate file size (max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if photo_file.size > max_size:
                return JsonResponse({'error': 'File size exceeds 5MB limit.'}, status=400)

            import os
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import uuid

            # Generate a unique filename
            ext = os.path.splitext(photo_file.name)[1]
            unique_filename = f"profile_photos/{uuid.uuid4()}{ext}"

            # Save the file
            saved_path = default_storage.save(unique_filename, ContentFile(photo_file.read()))

            # Update the profile with the new photo URL
            profile.photo_url = f"/media/{saved_path}"
        profile.save()
    else:
        # Handle JSON data
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

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

    # Return updated profile data
    return JsonResponse({
        'message': 'Profile updated successfully',
        'profile': {
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
    })


@csrf_exempt
@jwt_login_required
@require_roles('super_admin')
@require_http_methods(["GET"])
def manage_users(request):
    """List all users (super_admin only)."""

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
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
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
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            })

    return JsonResponse({'users': users_data})


@jwt_login_required
@require_http_methods(["GET"])
def system_status(request):
    """Return simple live health stats for the portal."""
    server_status = 'online'

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = 'online'
    except Exception:
        db_status = 'error'

    # Email check (detect configuration; best-effort ping)
    try:
        conn = get_connection()
        backend_path = f"{conn.__class__.__module__}.{conn.__class__.__name__}"
        # Treat console and in-memory backends as not configured for real delivery
        if 'console.EmailBackend' in backend_path or 'locmem.EmailBackend' in backend_path:
            email_status = 'not_configured'
        else:
            conn.open()
            email_status = 'online'
            conn.close()
    except Exception:
        email_status = 'error'

    data = {
        'checked_at': timezone.now().isoformat(),
        'server': server_status,
        'database': db_status,
        'email': email_status,
    }
    return JsonResponse(data)


@jwt_login_required
@require_http_methods(["GET"])
def active_today(request):
    """Return count of users who have been active today."""
    from django.utils import timezone
    import datetime
    
    # Get today's date
    today = timezone.now().date()
    
    # Count users who have been active today (based on last_activity in Profile)
    from .models import Profile
    active_count = Profile.objects.filter(
        last_activity__date=today
    ).count()
    
    data = {
        'active_today': active_count,
        'date': today.isoformat(),
        'timestamp': timezone.now().isoformat(),
    }
    return JsonResponse(data)


@jwt_login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Return notifications for the current user."""
    from .models import Notification
    
    # Get all notifications for the current user, ordered by newest first
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]  # Limit to last 20
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'read_at': notification.read_at.isoformat() if notification.read_at else None
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': len([n for n in notifications_data if not n['is_read']])
    })


@csrf_exempt
@jwt_login_required
@require_http_methods(["POST"])
def mark_notification_as_read(request, notification_id):
    """Mark a specific notification as read."""
    from .models import Notification
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)


@csrf_exempt
@jwt_login_required
@require_http_methods(["POST"])
def mark_all_notifications_as_read(request):
    """Mark all notifications as read for the current user."""
    from .models import Notification
    
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({'success': True})


@csrf_exempt
@jwt_login_required
@require_roles('super_admin')
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


@csrf_exempt
@jwt_login_required
@require_roles('super_admin')
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


@csrf_exempt
@jwt_login_required
@require_roles('super_admin')
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


@csrf_exempt
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
