from django.contrib import admin
from apps.documents.models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'owner', 'status', 'uploaded_at_display', 'reviewed_at', 'reviewed_by')
    list_filter = ('status', 'document_type')
    search_fields = ('owner__name', 'owner__email', 'rejection_reason')
    raw_id_fields = ('owner', 'reviewed_by')
    ordering = ('-created_at',)

    def uploaded_at_display(self, obj):
        return obj.created_at
    uploaded_at_display.short_description = 'Enviado em'
