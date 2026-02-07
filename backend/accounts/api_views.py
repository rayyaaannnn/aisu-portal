"""
Example API views demonstrating the use of RoleRequiredPermission.
These views require Django REST Framework to be installed.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import RoleRequiredPermission
from .models import Designation
from .serializers import DesignationSerializer


class UserInfoView(APIView):
    """
    Get current authenticated user's info including role.
    Used by React frontend for role-based redirects after login.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        try:
            profile = request.user.profile
            return Response({
                'username': request.user.username,
                'email': request.user.email,
                'role': profile.role,
                'state': profile.state,
                'district': profile.district,
            })
        except Exception as e:
            return Response({
                'username': request.user.username,
                'role': 'district_team'  # Default role
            })


class AdminOnlyView(APIView):
    """
    View that only super_admins can access.
    
    Usage:
        class MyView(APIView):
            permission_classes = [RoleRequiredPermission]
            required_role = 'super_admin'
    """
    permission_classes = [RoleRequiredPermission]
    required_role = 'super_admin'
    
    def get(self, request):
        return Response({
            'message': 'Welcome, Super Admin!',
            'user': request.user.username,
            'role': request.user.profile.role
        })


class ITTeamView(APIView):
    """
    View that only IT Team members can access.
    """
    permission_classes = [RoleRequiredPermission]
    required_role = 'it_team'
    
    def get(self, request):
        return Response({
            'message': 'Welcome, IT Team Member!',
            'user': request.user.username,
            'role': request.user.profile.role
        })


class StateTeamView(APIView):
    """
    View that only State Team members can access.
    """
    permission_classes = [RoleRequiredPermission]
    required_role = 'state_team'
    
    def get(self, request):
        return Response({
            'message': 'Welcome, State Team Member!',
            'user': request.user.username,
            'role': request.user.profile.role,
            'state': request.user.profile.state
        })


class DistrictTeamView(APIView):
    """
    View that only District Team members can access.
    """
    permission_classes = [RoleRequiredPermission]
    required_role = 'district_team'
    
    def get(self, request):
        return Response({
            'message': 'Welcome, District Team Member!',
            'user': request.user.username,
            'role': request.user.profile.role,
            'district': request.user.profile.district
        })


class MultipleRolesView(APIView):
    """
    View that allows multiple roles using a list.
    
    Usage:
        class MyView(APIView):
            permission_classes = [RoleRequiredPermission]
            required_role = ['super_admin', 'it_team']
    """
    permission_classes = [RoleRequiredPermission]
    required_role = ['super_admin', 'it_team']
    
    def get(self, request):
        return Response({
            'message': 'Welcome! You have elevated privileges.',
            'user': request.user.username,
            'role': request.user.profile.role
        })


class DesignationViewSet(viewsets.ModelViewSet):
    """
    API viewset for Designation model.
    
    Provides list and retrieve endpoints:
    - GET /api/designations/ - List all designations
    - GET /api/designations/{id}/ - Retrieve a specific designation
    
    Uses default permissions (IsAuthenticatedOrReadOnly).
    """
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        # Super admins and IT team can mutate; others read-only
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [RoleRequiredPermission]
            self.required_role = ['super_admin', 'it_team']
        return super().get_permissions()
