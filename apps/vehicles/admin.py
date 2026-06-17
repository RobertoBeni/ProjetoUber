from django.contrib import admin
from apps.vehicles.models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate', 'brand', 'model', 'year', 'vehicle_type', 'body_type', 'status', 'owner_driver')
    list_filter = ('status', 'vehicle_type', 'body_type', 'has_insurance')
    search_fields = ('plate', 'renavam', 'brand', 'model', 'owner_driver__email', 'owner_driver__name')
    raw_id_fields = ('owner_driver', 'carrier_company')
    ordering = ('-created_at',)
