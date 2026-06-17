from django.contrib import admin
from apps.tracking.models import TrackingEvent

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = (
        'id_truncated',
        'freight_order_link',
        'event_type',
        'driver',
        'vehicle',
        'speed',
        'latitude',
        'longitude',
        'created_at'
    )
    list_filter = ('event_type', 'created_at')
    search_fields = (
        'id',
        'freight_order__id',
        'driver__name',
        'driver__email',
        'vehicle__plate'
    )
    readonly_fields = ('created_at', 'updated_at')

    def id_truncated(self, obj):
        return f"{str(obj.id)[:8]}..."
    id_truncated.short_description = "ID"

    def freight_order_link(self, obj):
        return f"Frete {str(obj.freight_order.id)[:8]}..."
    freight_order_link.short_description = "Ordem de Frete"
