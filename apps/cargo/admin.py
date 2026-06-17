from django.contrib import admin
from apps.cargo.models import CargoType, CargoRule

class CargoRuleInline(admin.StackedInline):
    model = CargoRule
    can_delete = False
    verbose_name_plural = 'Regra de Compatibilidade'

@admin.register(CargoType)
class CargoTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CargoRuleInline]
    ordering = ('name',)

@admin.register(CargoRule)
class CargoRuleAdmin(admin.ModelAdmin):
    list_display = ('cargo_type', 'requires_covered_vehicle', 'requires_grain_body', 'requires_helper_recommended', 'requires_insurance_recommended')
    list_filter = ('requires_covered_vehicle', 'requires_grain_body', 'requires_helper_recommended', 'requires_insurance_recommended')
    search_fields = ('cargo_type__name',)
