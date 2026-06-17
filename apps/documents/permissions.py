from rest_framework import permissions

class IsDocumentOwnerOrStaff(permissions.BasePermission):
    """
    Object-level permission to only allow owners or support/admin staff to view/edit a document.
    """
    def has_object_permission(self, request, view, obj):
        # Allow superusers, ADMINs or SUPPORT operators
        if request.user.is_superuser or request.user.user_type in ['ADMIN', 'SUPPORT']:
            return True
        # Allow owner of the document
        return obj.owner == request.user
