from django.contrib import admin
from apps.support.models import SupportTicket

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        'id_truncated',
        'user',
        'freight_order_link',
        'category',
        'priority',
        'status',
        'assigned_to',
        'created_from',
        'created_at'
    )
    list_filter = ('category', 'priority', 'status', 'created_from', 'created_at')
    search_fields = (
        'id',
        'user__name',
        'user__email',
        'freight_order__id',
        'description'
    )
    readonly_fields = ('created_at', 'updated_at', 'closed_at')

    def id_truncated(self, obj):
        return f"{str(obj.id)[:8]}..."
    id_truncated.short_description = "ID"

    def freight_order_link(self, obj):
        if obj.freight_order:
            return f"Frete {str(obj.freight_order.id)[:8]}..."
        return "Nenhum"
    freight_order_link.short_description = "Ordem de Frete"
