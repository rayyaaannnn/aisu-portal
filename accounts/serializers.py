from rest_framework import serializers
from .models import Designation


class DesignationSerializer(serializers.ModelSerializer):
    """Serializer for Designation model with nested parent designation."""
    
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Designation
        fields = [
            'id',
            'name',
            'level',
            'level_display',
            'department',
            'description',
            'responsibilities',
            'authority',
            'accountability',
            'parent',
            'parent_name',
        ]
        read_only_fields = ['id', 'level_display', 'parent_name']
