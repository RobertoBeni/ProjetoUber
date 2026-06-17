from django.contrib import admin
from apps.pricing.models import PriceEstimate

@admin.register(PriceEstimate)
class PriceEstimateAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'cargo_type', 'vehicle_type', 
        'distance_km', 'total_estimated_price', 'created_at'
    )
    list_filter = ('vehicle_type', 'created_at')
    search_fields = ('id', 'customer__name', 'customer__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
