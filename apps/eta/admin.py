from django.contrib import admin
from apps.eta.models import ETARecord

@admin.register(ETARecord)
class ETARecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'freight_order', 'estimated_arrival_time', 
        'remaining_distance_km', 'remaining_duration_minutes', 
        'average_speed_kmh', 'reason', 'created_at'
    )
    list_filter = ('reason', 'created_at')
    search_fields = ('id', 'freight_order__id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
