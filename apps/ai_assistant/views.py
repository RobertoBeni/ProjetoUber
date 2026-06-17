from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.ai_assistant.models import AIConversation, AIMessage
from apps.ai_assistant.serializers import AIConversationSerializer, AIMessageSerializer
from apps.ai_assistant.services import AIOrchestrator
from django.utils import timezone

class AIConversationViewSet(viewsets.ModelViewSet):
    serializer_class = AIConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view their own conversations unless they are staff
        if self.request.user.is_staff:
            return AIConversation.objects.all()
        return AIConversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='escalate')
    def escalate(self, request, pk=None):
        conversation = self.get_object()
        if conversation.status == 'escalated':
            return Response({"detail": "Esta conversa já está escalonada para atendimento humano."}, status=status.HTTP_400_BAD_REQUEST)
        
        conversation.status = 'escalated'
        conversation.save(update_fields=['status'])

        # Add a system message notifying user
        AIMessage.objects.create(
            conversation=conversation,
            sender='system',
            message_text="Esta conversa foi transferida para nossa equipe de atendimento humano. Por favor, aguarde, um operador entrará em contato em instantes."
        )

        return Response(AIConversationSerializer(conversation).data, status=status.HTTP_200_OK)

class AIChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message_text = request.data.get('message_text')
        conversation_id = request.data.get('conversation_id')
        channel = request.data.get('channel', 'web')

        if not message_text:
            return Response({"detail": "O campo message_text é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # Call orchestrator
        try:
            assistant_msg = AIOrchestrator.process_message(
                user=request.user,
                conversation_id=conversation_id,
                message_text=message_text,
                channel=channel
            )
            serializer = AIMessageSerializer(assistant_msg)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
