import re
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Standard serializer for User model representation.
    """
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'phone', 'document_type', 
            'document_number', 'user_type', 'is_verified', 
            'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at']

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for User self-registration.
    """
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'document_type', 'document_number', 'user_type', 'password']

    def validate_document_number(self, value):
        # Strips dots, dashes, slashes
        clean_value = re.sub(r'[^0-9]', '', value)
        
        # Validates basic format length
        if self.initial_data.get('document_type') == 'CPF' and len(clean_value) != 11:
            raise serializers.ValidationError("O CPF deve conter exatamente 11 dígitos numéricos.")
        elif self.initial_data.get('document_type') == 'CNPJ' and len(clean_value) != 14:
            raise serializers.ValidationError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
            
        return clean_value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Já existe um usuário cadastrado com este e-mail.")
        return value.lower()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating the user profile.
    """
    class Meta:
        model = User
        fields = ['name', 'phone', 'document_type', 'document_number']

    def validate_document_number(self, value):
        clean_value = re.sub(r'[^0-9]', '', value)
        doc_type = self.initial_data.get('document_type') or getattr(self.instance, 'document_type')
        
        if doc_type == 'CPF' and len(clean_value) != 11:
            raise serializers.ValidationError("O CPF deve conter exatamente 11 dígitos numéricos.")
        elif doc_type == 'CNPJ' and len(clean_value) != 14:
            raise serializers.ValidationError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
            
        return clean_value

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT obtain serializer that appends user details to the response.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        # Include serialized user payload
        data['user'] = UserSerializer(self.user).data
        return data

from apps.accounts.models import UserConsent

class UserConsentSerializer(serializers.ModelSerializer):
    consent_type_display = serializers.CharField(source='get_consent_type_display', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = UserConsent
        fields = ['id', 'user', 'user_name', 'consent_type', 'consent_type_display', 'accepted', 'version', 'accepted_at', 'ip_address']
        read_only_fields = ['id', 'user', 'user_name', 'consent_type_display', 'accepted_at']

