from rest_framework import permissions

class IsPFClient(permissions.BasePermission):
    """Allows access only to PF Clients (Pessoa Física)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'PF'

class IsPJClient(permissions.BasePermission):
    """Allows access only to PJ Clients (Pessoa Jurídica)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'PJ'

class IsDriver(permissions.BasePermission):
    """Allows access only to Drivers (Motoristas)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'DRIVER'

class IsCarrier(permissions.BasePermission):
    """Allows access only to Carrier Companies (Transportadoras)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'CARRIER'

class IsAdminUserType(permissions.BasePermission):
    """Allows access to Platform Administrators."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.user_type == 'ADMIN' or request.user.is_superuser)

class IsSupportOperator(permissions.BasePermission):
    """Allows access only to Support Operators."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.user_type in ['SUPPORT', 'ADMIN'] or request.user.is_superuser)

class IsFinanceOperator(permissions.BasePermission):
    """Allows access only to Finance Operators."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.user_type in ['FINANCE', 'ADMIN'] or request.user.is_superuser)

class IsLogisticsOperator(permissions.BasePermission):
    """Allows access only to Logistics Operators."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.user_type in ['LOGISTICS', 'ADMIN'] or request.user.is_superuser)
