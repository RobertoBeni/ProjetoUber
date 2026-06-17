from apps.audit.models import AuditLog

def create_audit_log(user, action, entity_type, entity_id=None, request=None, metadata=None):
    """
    Utility service to create system audit logs with automatic IP and User-Agent extraction.
    """
    ip_address = None
    user_agent = None

    if request is not None:
        # Extract IP address checking for reverse proxies
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Extract User Agent
        user_agent = request.META.get('HTTP_USER_AGENT')

    return AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else "",
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata or {}
    )
