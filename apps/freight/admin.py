from django.contrib import admin
from apps.freight.models import FreightOrder, CargoItem

class CargoItemInline(admin.TabularInline):
    model = CargoItem
    extra = 1

@admin.register(FreightOrder)
class FreightOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'driver', 'status', 'cargo_category', 
        'estimated_weight_kg', 'estimated_price', 'final_price', 'created_at'
    )
    list_filter = ('status', 'cargo_category', 'requires_helper', 'requires_insurance', 'created_at')
    search_fields = ('id', 'customer__name', 'customer__email', 'driver__name', 'origin_address', 'destination_address')
    inlines = [CargoItemInline]
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CargoItem)
class CargoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'freight_order', 'cargo_type', 'description', 'estimated_weight_kg', 'quantity')
    list_filter = ('cargo_type', 'is_fragile', 'requires_helper', 'requires_insurance')
    search_fields = ('description', 'freight_order__id')
