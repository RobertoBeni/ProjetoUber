from django.contrib import admin
from apps.companies.models import CompanyProfile, CarrierCompany

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for CompanyProfile (PJ Clients).
    """
    list_display = (
        'trade_name', 'cnpj', 'user', 'responsible_name', 
        'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'legal_name', 'trade_name', 'cnpj', 
        'responsible_name', 'user__email'
    )
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('id', 'user', 'status')}),
        ('Informações Corporativas', {
            'fields': ('legal_name', 'trade_name', 'cnpj', 'state_registration')
        }),
        ('Responsável de Contato', {
            'fields': ('responsible_name', 'responsible_phone')
        }),
        ('Endereços', {
            'fields': ('billing_address', 'operational_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(CarrierCompany)
class CarrierCompanyAdmin(admin.ModelAdmin):
    """
    Admin configuration for CarrierCompany (Transportadoras).
    """
    list_display = (
        'trade_name', 'cnpj', 'owner_user', 'responsible_name', 
        'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'legal_name', 'trade_name', 'cnpj', 
        'responsible_name', 'owner_user__email'
    )
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('id', 'owner_user', 'status')}),
        ('Informações da Transportadora', {
            'fields': ('legal_name', 'trade_name', 'cnpj', 'state_registration')
        }),
        ('Responsável de Contato', {
            'fields': ('responsible_name', 'responsible_phone')
        }),
        ('Endereços', {
            'fields': ('billing_address', 'operational_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
