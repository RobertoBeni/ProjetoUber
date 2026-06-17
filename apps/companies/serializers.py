import re
from rest_framework import serializers
from apps.companies.models import CompanyProfile, CarrierCompany

class CompanyProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for CompanyProfile representation and validation.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = CompanyProfile
        fields = [
            'id', 'user', 'user_email', 'legal_name', 'trade_name', 'cnpj', 
            'state_registration', 'responsible_name', 'responsible_phone', 
            'billing_address', 'operational_address', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']

    def validate_cnpj(self, value):
        clean_value = re.sub(r'[^0-9]', '', value)
        if len(clean_value) != 14:
            raise serializers.ValidationError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
        return clean_value

class CarrierCompanySerializer(serializers.ModelSerializer):
    """
    Serializer for CarrierCompany representation and validation.
    """
    owner_email = serializers.EmailField(source='owner_user.email', read_only=True)

    class Meta:
        model = CarrierCompany
        fields = [
            'id', 'owner_user', 'owner_email', 'legal_name', 'trade_name', 'cnpj', 
            'state_registration', 'responsible_name', 'responsible_phone', 
            'billing_address', 'operational_address', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner_user', 'status', 'created_at', 'updated_at']

    def validate_cnpj(self, value):
        clean_value = re.sub(r'[^0-9]', '', value)
        if len(clean_value) != 14:
            raise serializers.ValidationError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
        return clean_value
