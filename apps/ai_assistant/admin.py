from django.contrib import admin
from apps.ai_assistant.models import AIConversation, AIMessage, AIAction, KnowledgeDocument, KnowledgeEmbedding

class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    readonly_fields = ('created_at',)

class AIActionInline(admin.TabularInline):
    model = AIAction
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('id_truncated', 'user', 'channel', 'status', 'created_at')
    list_filter = ('channel', 'status', 'created_at')
    search_fields = ('id', 'user__name', 'user__email')
    inlines = [AIMessageInline, AIActionInline]

    def id_truncated(self, obj):
        return f"{str(obj.id)[:8]}..."
    id_truncated.short_description = "ID"

@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation_link', 'sender', 'message_truncated', 'intent', 'confidence_score', 'created_at')
    list_filter = ('sender', 'intent', 'created_at')
    search_fields = ('message_text', 'intent', 'conversation__id')

    def conversation_link(self, obj):
        return f"Conversa {str(obj.conversation.id)[:8]}..."
    conversation_link.short_description = "Conversa"

    def message_truncated(self, obj):
        return f"{obj.message_text[:50]}..." if len(obj.message_text) > 50 else obj.message_text
    message_truncated.short_description = "Mensagem"

@admin.register(AIAction)
class AIActionAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'user', 'action_type', 'target_entity', 'status', 'requires_confirmation', 'created_at')
    list_filter = ('action_type', 'status', 'requires_confirmation')
    search_fields = ('action_type', 'target_entity', 'target_id', 'conversation__id')

@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'version', 'status', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'content', 'category')

@admin.register(KnowledgeEmbedding)
class KnowledgeEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('document', 'created_at')
    search_fields = ('document__title',)
