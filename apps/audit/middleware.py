from apps.audit.services import create_audit_log

class AuditMiddleware:
    """
    Middleware that automatically audits write operations (POST, PUT, PATCH, DELETE)
    performed by authenticated users, capturing path, entity contexts, and response status.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Audit only authenticated write methods, skipping explicit endpoints
        if (
            hasattr(request, 'user') and 
            request.user and 
            request.user.is_authenticated and 
            request.method in ['POST', 'PUT', 'PATCH', 'DELETE']
        ):
            path = request.path
            # Avoid duplicate logs for explicit logins/registers/logouts which are logged explicitly
            if not any(x in path for x in ['/auth/login/', '/auth/register/', '/auth/logout/']):
                # Try to extract a potential entity ID from path
                entity_id = ""
                path_parts = [p for p in path.split('/') if p]
                if path_parts:
                    last_part = path_parts[-1]
                    # If last part is not a action verb, it might be a UUID/ID
                    if len(last_part) > 2:
                        entity_id = last_part

                create_audit_log(
                    user=request.user,
                    action=f"Requisição {request.method} em {path}",
                    entity_type="API_WRITE_ACTION",
                    entity_id=entity_id,
                    request=request,
                    metadata={"status_code": response.status_code}
                )

        return response

