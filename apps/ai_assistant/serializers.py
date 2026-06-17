from rest_framework import serializers
from apps.ai_assistant.models import AIConversation, AIMessage, AIAction, KnowledgeDocument

class AIMessageSerializer(serializers.ModelSerializer):
    sender_display = serializers.CharField(source='get_sender_display', read_only=True)
    
    class Meta:
        model = AIMessage
        fields = ['id', 'conversation', 'sender', 'sender_display', 'message_text', 'intent', 'confidence_score', 'metadata', 'created_at']
        read_only_fields = ['id', 'sender_display', 'intent', 'confidence_score', 'metadata', 'created_at']

class AIConversationSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = AIConversation
        fields = ['id', 'user', 'user_name', 'channel', 'channel_display', 'status', 'status_display', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'user_name', 'channel_display', 'status_display', 'messages', 'created_at', 'updated_at']

class AIActionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AIAction
        fields = ['id', 'conversation', 'user', 'action_type', 'target_entity', 'target_id', 'status', 'status_display', 'requires_confirmation', 'confirmed_at', 'created_at']
        read_only_fields = ['id', 'status_display', 'confirmed_at', 'created_at']

class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeDocument
        fields = ['id', 'title', 'category', 'content', 'version', 'status', 'created_at']
