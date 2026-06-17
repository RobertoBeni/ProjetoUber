from django.contrib import admin
from apps.routing.models import Route

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'freight_order', 'provider', 'distance_km', 
        'duration_minutes', 'toll_estimate', 'created_at'
    )
    list_filter = ('provider', 'created_at')
    search_fields = ('id', 'freight_order__id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
