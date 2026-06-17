from django.contrib import admin
from apps.matching.models import MatchCandidate

@admin.register(MatchCandidate)
class MatchCandidateAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'freight_order', 'driver', 'vehicle', 
        'distance_to_pickup_km', 'final_score', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'freight_order__id', 'driver__name', 'driver__email', 'vehicle__plate')
    ordering = ('-final_score',)
    readonly_fields = ('created_at', 'updated_at')
