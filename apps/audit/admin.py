from django.contrib import admin
from apps.audit.models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for AuditLog.
    Logs are strictly read-only within the Django Admin to prevent tampering.
    """
    list_display = (
        'created_at', 'user', 'action', 'entity_type', 
        'entity_id', 'ip_address'
    )
    list_filter = ('action', 'entity_type', 'created_at')
    search_fields = (
        'user__email', 'action', 'entity_type', 
        'entity_id', 'ip_address', 'user_agent'
    )
    ordering = ('-created_at',)

    # Restrict permissions to guarantee log immutability
    readonly_fields = (
        'id', 'user', 'action', 'entity_type', 'entity_id', 
        'ip_address', 'user_agent', 'metadata', 'created_at', 'updated_at'
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
