from rest_framework import serializers
from apps.documents.models import Document

class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model representation and validation.
    Prevents direct updating of status and review fields.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'owner', 'owner_email', 'owner_name', 'document_type',
            'file', 'status', 'reviewed_at', 'reviewed_by', 'reviewed_by_email',
            'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'status', 'reviewed_at', 'reviewed_by',
            'created_at', 'updated_at'
        ]
