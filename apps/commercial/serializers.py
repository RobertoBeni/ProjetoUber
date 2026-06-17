from rest_framework import serializers
from apps.commercial.models import InvestorLead

class InvestorLeadSerializer(serializers.ModelSerializer):
    profile_type_display = serializers.CharField(source='get_profile_type_display', read_only=True)
    estimated_interest_level_display = serializers.CharField(source='get_estimated_interest_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = InvestorLead
        fields = [
            'id', 'name', 'email', 'phone', 'company', 'profile_type', 'profile_type_display',
            'estimated_interest_level', 'estimated_interest_level_display', 'message',
            'source_page', 'status', 'status_display', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'profile_type_display', 'estimated_interest_level_display', 'status_display',
            'created_at', 'updated_at'
        ]

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("O e-mail é obrigatório.")
        return value.lower()
