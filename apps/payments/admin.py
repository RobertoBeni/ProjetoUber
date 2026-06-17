from django.contrib import admin
from apps.payments.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'freight_order', 'payer', 'driver', 
        'amount', 'platform_fee', 'driver_amount', 
        'status', 'payment_method', 'transaction_id', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('id', 'freight_order__id', 'payer__name', 'driver__name', 'transaction_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
