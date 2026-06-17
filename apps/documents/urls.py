from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.documents.views import DocumentViewSet

router = DefaultRouter()
router.register('documents', DocumentViewSet, basename='document')

admin_review_action = DocumentViewSet.as_view({'patch': 'review'})

urlpatterns = [
    path('', include(router.urls)),
    path('admin/documents/<uuid:pk>/review/', admin_review_action, name='admin-document-review'),
]
