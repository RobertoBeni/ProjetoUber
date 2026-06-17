from rest_framework.renderers import JSONRenderer

class StandardJSONRenderer(JSONRenderer):
    """
    Custom DRF renderer that enforces a standard API response format for all endpoints:
    
    Success (2xx):
    {
      "success": true,
      "data": {...},
      "message": "Operação realizada com sucesso."
    }
    
    Error (4xx/5xx):
    {
      "success": false,
      "errors": {...},
      "message": "Erro ao processar solicitação."
    }
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        
        # Enforce standard formatting
        success = True
        message = "Operação realizada com sucesso."
        errors = {}
        payload = data

        if response is not None:
            status_code = response.status_code
            if status_code >= 400:
                success = False
                message = "Erro ao processar solicitação."
                
                # DRF error details extraction
                if isinstance(data, dict):
                    # Check for generic DRF error details
                    detail = data.get('detail') or data.get('message')
                    if detail:
                        message = str(detail)
                    errors = data
                else:
                    errors = {"non_field_errors": data}
                payload = {}
            else:
                # If the view response data is already a dict, extract custom message/data
                if isinstance(data, dict):
                    # Check if standard format was manually returned by view
                    if 'success' in data and ('data' in data or 'errors' in data):
                        return super().render(data, accepted_media_type, renderer_context)
                    
                    message = data.pop('message', message)
                    # If 'data' is the only remaining key, extract it
                    if 'data' in data and len(data) == 1:
                        payload = data['data']
                    else:
                        payload = data

        formatted_data = {
            "success": success,
            "data": payload if success else {},
            "errors": errors if not success else {},
            "message": message
        }

        return super().render(formatted_data, accepted_media_type, renderer_context)
