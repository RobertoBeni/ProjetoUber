from rest_framework import permissions

class IsFreightParticipant(permissions.BasePermission):
    """
    Object-level permission to ensure only relevant customers, assigned or eligible drivers,
    carrier companies, and system administrators can view or transition freight orders.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
            
        # Superuser and Staff always allowed
        if user.is_staff or user.is_superuser:
            return True
            
        # Client who solicited the freight
        if obj.customer == user:
            return True
            
        # Driver currently assigned
        if obj.driver == user:
            return True
            
        # Eligible drivers during waiting driver matching phase
        if obj.status == 'waiting_driver' and hasattr(user, 'driver_profile'):
            return True
            
        # Carrier companies associated
        if obj.carrier_company:
            if hasattr(user, 'carrier_company') and user.carrier_company == obj.carrier_company:
                return True
            if hasattr(user, 'driver_profile') and user.driver_profile.carrier_company == obj.carrier_company:
                return True
                
        return False
