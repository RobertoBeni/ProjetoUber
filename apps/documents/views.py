from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from apps.documents.models import Document
from apps.documents.serializers import DocumentSerializer
from apps.documents.permissions import IsDocumentOwnerOrStaff
from apps.accounts.permissions import IsSupportOperator
from apps.audit.services import create_audit_log

class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user Documents (CNH, CRLV, INVOICE, WEIGHING).
    Endpoints:
    - POST /api/documents/ (Authenticated users)
    - GET /api/documents/ (Filtered: owners only see theirs, support/admin see all)
    - GET/PATCH/DELETE /api/documents/{id}/ (Strictly owner or support/admin)
    - PATCH /api/documents/{id}/review/ (Only support/admin)
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDocumentOwnerOrStaff]

    def perform_create(self, serializer):
        # Automatically assign ownership and set default pending status
        serializer.save(owner=self.request.user, status='pending')
        # Audit creation
        document = serializer.instance
        create_audit_log(
            self.request.user, 
            f"Upload de Documento: {document.get_document_type_display()}", 
            "Document", 
            document.id, 
            self.request
        )

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.user_type in ['ADMIN', 'SUPPORT']:
            return Document.objects.all()
        if self.action == 'list':
            return Document.objects.filter(owner=user)
        return Document.objects.all()

    @action(detail=True, methods=['patch'], url_path='review', permission_classes=[IsSupportOperator])
    def review(self, request, pk=None):
        """
        Endpoint: PATCH /api/documents/{id}/review/
        Allows Support operators or Admins to approve/reject a document.
        """
        document = self.get_object()
        status_value = request.data.get('status')
        rejection_reason = request.data.get('rejection_reason', '')

        if status_value not in ['approved', 'rejected', 'pending']:
            return Response(
                {"detail": "Status de revisão inválido. Opções: approved, rejected, pending."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if status_value == 'rejected' and not rejection_reason:
            return Response(
                {"detail": "O campo 'rejection_reason' é obrigatório para documentos rejeitados."},
                status=status.HTTP_400_BAD_REQUEST
            )

        document.status = status_value
        document.rejection_reason = rejection_reason if status_value == 'rejected' else ''
        document.reviewed_at = timezone.now()
        document.reviewed_by = request.user
        document.save()

        # Audit review action
        create_audit_log(
            request.user,
            f"Revisão de Documento: {status_value.upper()}",
            "Document",
            document.id,
            request,
            metadata={"document_type": document.document_type, "owner_email": document.owner.email}
        )

        serializer = self.get_serializer(document)
        return Response(
            {
                "message": f"Status do documento alterado para {status_value}.",
                "data": serializer.data
            }
        )
