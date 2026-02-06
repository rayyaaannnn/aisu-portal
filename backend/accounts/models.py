from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role')
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class Profile(models.Model):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('it_team', 'IT Team'),
        ('state_team', 'State Team'),
        ('district_team', 'District Team'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    state = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    photo_url = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Designation(models.Model):
    """Model to represent organizational roles/designations."""
    
    LEVEL_CHOICES = (
        ('national', 'National'),
        ('state', 'State'),
        ('district', 'District'),
        ('mandal', 'Mandal'),
        ('college', 'College'),
    )
    
    name = models.CharField(max_length=100, help_text="e.g., National President")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True, 
                                   help_text="e.g., Social Media, Press, IT Cell, Legal")
    description = models.TextField(blank=True, null=True, 
                                    help_text="Short summary of the role")
    responsibilities = models.TextField(help_text="List of responsibilities")
    authority = models.TextField(help_text="Authority and powers")
    accountability = models.TextField(help_text="Accountability and duties")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, 
                               blank=True, null=True, 
                               related_name='children',
                               help_text="Parent designation for hierarchy")
    
    class Meta:
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'
        ordering = ['level', 'name']
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.name}"
