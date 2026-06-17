from rest_framework import viewsets, mixins, permissions
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.accounts.permissions import IsAdminUserType, IsSupportOperator

class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Read-only viewset for system Audit Logs.
    Only accessible by Administrators or Support Operators.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserType | IsSupportOperator]
