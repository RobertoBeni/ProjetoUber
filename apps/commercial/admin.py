from django.contrib import admin
from apps.commercial.models import InvestorLead

@admin.register(InvestorLead)
class InvestorLeadAdmin(admin.ModelAdmin):
    list_display = (
        'id_truncated',
        'name',
        'email',
        'company',
        'profile_type',
        'estimated_interest_level',
        'status',
        'created_at'
    )
    list_filter = ('profile_type', 'estimated_interest_level', 'status', 'created_at')
    search_fields = (
        'id',
        'name',
        'email',
        'company',
        'message',
        'notes'
    )
    readonly_fields = ('created_at', 'updated_at')

    def id_truncated(self, obj):
        return f"{str(obj.id)[:8]}..."
    id_truncated.short_description = "ID"
