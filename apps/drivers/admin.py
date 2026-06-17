from django.contrib import admin
from apps.drivers.models import DriverProfile

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cnh_number', 'cnh_category', 'cnh_expiration_date', 'status', 'is_online', 'rating')
    list_filter = ('status', 'cnh_category', 'is_online')
    search_fields = ('user__name', 'user__email', 'cnh_number')
    raw_id_fields = ('user', 'carrier_company')
    ordering = ('-created_at',)
