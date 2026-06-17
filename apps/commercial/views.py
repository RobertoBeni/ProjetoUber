from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.commercial.models import InvestorLead
from apps.commercial.serializers import InvestorLeadSerializer
from apps.audit.services import create_audit_log

class IsCommercialStaff(permissions.BasePermission):
    """
    Allows access only to authenticated users with ADMIN, SUPPORT, or LOGISTICS roles.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser and staff always have permission
        if request.user.is_superuser or request.user.is_staff:
            return True
            
        # Role check
        allowed_roles = ['ADMIN', 'SUPPORT', 'LOGISTICS']
        return getattr(request.user, 'user_type', None) in allowed_roles


class InvestorLeadViewSet(viewsets.ModelViewSet):
    queryset = InvestorLead.objects.all()
    serializer_class = InvestorLeadSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Public endpoint
            return [permissions.AllowAny()]
        return [IsCommercialStaff()]

    def perform_create(self, serializer):
        lead = serializer.save()
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        
        # Log lead creation in AuditLog
        create_audit_log(
            user=user,
            action="CREATE_LEAD",
            entity_type="InvestorLead",
            entity_id=lead.id,
            request=self.request,
            metadata={
                "name": lead.name,
                "email": lead.email,
                "profile_type": lead.profile_type,
                "company": lead.company,
                "estimated_interest_level": lead.estimated_interest_level
            }
        )

    def perform_update(self, serializer):
        old_lead = self.get_object()
        old_status = old_lead.status
        old_notes = old_lead.notes
        
        lead = serializer.save()
        
        # Log lead update in AuditLog
        create_audit_log(
            user=self.request.user,
            action="UPDATE_LEAD",
            entity_type="InvestorLead",
            entity_id=lead.id,
            request=self.request,
            metadata={
                "previous_status": old_status,
                "new_status": lead.status,
                "notes_updated": old_notes != lead.notes
            }
        )
