from rest_framework.permissions import BasePermission


class RoleRequiredPermission(BasePermission):
    """
    Permission class that checks if the authenticated user has the required role.
    
    The required role should be defined as a `required_role` attribute on the view.
    Supports both single role (string) and multiple roles (list/tuple).
    
    Usage:
        # Single role
        class MyView(APIView):
            permission_classes = [RoleRequiredPermission]
            required_role = 'admin'
            
        # Multiple roles (user must have at least one)
        class MyView(APIView):
            permission_classes = [RoleRequiredPermission]
            required_role = ['admin', 'moderator']
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has the required role.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get the required role(s) from the view
        required_role = getattr(view, 'required_role', None)
        
        if required_role is None:
            # If no required_role is defined, deny access by default
            return False
        
        # Check if user has a profile
        if not hasattr(request.user, 'profile'):
            return False
        
        # Check if user's role matches the required role(s)
        user_role = getattr(request.user.profile, 'role', None)
        
        if user_role is None:
            return False
        
        # Support multiple roles (list or tuple)
        if isinstance(required_role, (list, tuple)):
            return user_role in required_role
        
        # Single role (string)
        return user_role == required_role
    
    def get_denied_message(self, request, view):
        """
        Return a custom error message when permission is denied.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            
        Returns:
            str: Error message explaining why access was denied
        """
        required_role = getattr(view, 'required_role', 'unknown')
        
        if not request.user or not request.user.is_authenticated:
            return "Authentication credentials were not provided."
        
        if not hasattr(request.user, 'profile'):
            return "User profile not found. Access denied."
        
        user_role = getattr(request.user.profile, 'role', None)
        
        if user_role is None:
            return "User has no role assigned. Access denied."
        
        # Format message for multiple roles
        if isinstance(required_role, (list, tuple)):
            roles_str = ', '.join(f"'{r}'" for r in required_role)
            return f"Access denied. You must have one of the following roles: {roles_str}"
        
        return f"Access denied. You must have the '{required_role}' role to access this resource."

