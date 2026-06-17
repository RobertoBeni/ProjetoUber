from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Custom Admin interface for User model.
    """
    list_display = (
        'email', 'name', 'phone', 'user_type', 
        'is_verified', 'is_active', 'is_staff', 'created_at'
    )
    list_filter = (
        'user_type', 'is_verified', 'is_active', 
        'is_staff', 'created_at'
    )
    search_fields = (
        'email', 'name', 'phone', 'document_number'
    )
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        ('Informações Cadastrais', {
            'fields': ('name', 'phone', 'document_type', 'document_number')
        }),
        ('Status & Permissões', {
            'fields': ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Automatically hash passwords if set via admin form
        if form.cleaned_data.get('password') and not change:
            obj.set_password(form.cleaned_data.get('password'))
        elif form.cleaned_data.get('password') and change:
            # Check if password has changed
            original = User.objects.get(pk=obj.pk)
            if original.password != obj.password:
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

from apps.accounts.models import UserConsent

@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_type', 'accepted', 'version', 'accepted_at', 'ip_address')
    list_filter = ('consent_type', 'accepted', 'accepted_at')
    search_fields = ('user__name', 'user__email', 'ip_address', 'version')
    readonly_fields = ('accepted_at',)
