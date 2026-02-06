from django.contrib import admin
from .models import Profile, Designation


class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'department', 'parent')
    list_filter = ('level', 'department')
    search_fields = ('name', 'description')
    raw_id_fields = ('parent',)


admin.site.register(Profile)
admin.site.register(Designation, DesignationAdmin)
