from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Custom customized Django Admin panel
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.companies.urls')),
    path('api/', include('apps.audit.urls')),
    
    # Skeletal routing placeholders for other apps (Module 2-5)
    path('api/drivers/', include('apps.drivers.urls')),
    path('api/vehicles/', include('apps.vehicles.urls')),
    path('api/cargo/', include('apps.cargo.urls')),
    path('api/', include('apps.freight.urls')),
    path('api/', include('apps.pricing.urls')),
    path('api/', include('apps.matching.urls')),
    path('api/', include('apps.routing.urls')),
    path('api/tracking/', include('apps.tracking.urls')),
    path('api/', include('apps.eta.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/', include('apps.notifications.urls')),
    path('api/support/', include('apps.support.urls')),
    path('api/ai/', include('apps.ai_assistant.urls')),
    path('api/', include('apps.commercial.urls')),
    
    # Portals and core web templates
    path('', include('apps.core.urls')),
]
