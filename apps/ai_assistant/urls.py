from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ai_assistant.views import AIConversationViewSet, AIChatView

router = DefaultRouter()
router.register('conversations', AIConversationViewSet, basename='ai-conversations')

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai-chat-api'),
    path('', include(router.urls)),
]
