from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import Profile


class UpdateLastActivityMiddleware(MiddlewareMixin):
    """
    Middleware to update the last_activity field for authenticated users
    on each request.
    """
    def process_request(self, request):
        # Only update for authenticated users
        if request.user and request.user.is_authenticated:
            try:
                # Update the last_activity field for the user's profile
                profile = Profile.objects.get(user=request.user)
                profile.last_activity = timezone.now()
                profile.save(update_fields=['last_activity'])  # Only update this field
            except Profile.DoesNotExist:
                # If profile doesn't exist, create one (though this shouldn't happen in practice)
                pass
        return None