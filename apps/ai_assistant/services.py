import re
import math
import hashlib
import json
import datetime
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal

from apps.ai_assistant.models import AIConversation, AIMessage, AIAction, KnowledgeDocument, KnowledgeEmbedding
from apps.support.models import SupportTicket
from apps.freight.models import FreightOrder
from apps.tracking.services import RedisTrackingClient

class IntentClassifier:
    """
    Analyzes message text and identifies the primary intent of the user.
    """
    @staticmethod
    def classify(text):
        text_lower = text.lower()
        
        # Track Order keywords
        track_keywords = [
            'onde esta', 'onde está', 'rastrear', 'posicao', 'posição', 'cade', 'cadê', 
            'rastreamento', 'localizacao', 'localização', 'caminho', 'entrega', 
            'onde ta', 'onde tá', 'acompanhar', 'meu frete', 'minha carga'
        ]
        
        # Recommend Vehicle keywords
        vehicle_keywords = [
            'recomendar', 'qual veiculo', 'qual veículo', 'veiculo ideal', 'veículo ideal', 
            'qual caminhão', 'qual caminhao', 'caminhão', 'caminhao', 'veículo', 'veiculo',
            'carroceria', 'carregar', 'levar', 'transportar', 'tipo de baú', 'tipo de bau'
        ]
        
        # Open Support Ticket keywords
        support_keywords = [
            'reclamar', 'abrir ticket', 'abrir chamado', 'suporte', 'problema', 'ajuda', 
            'avaria', 'avariad', 'danificad', 'atrasad', 'atraso', 'estragou', 'roubo', 'furtado', 
            'quebrou', 'quebrad', 'sinistro', 'divergencia', 'divergência', 'perdi', 'estornado'
        ]

        # Count keyword occurrences
        track_score = sum(1 for kw in track_keywords if kw in text_lower)
        vehicle_score = sum(1 for kw in vehicle_keywords if kw in text_lower)
        support_score = sum(1 for kw in support_keywords if kw in text_lower)

        # Boost support if strong indicators exist
        if any(w in text_lower for w in ['avariad', 'quebrad', 'danificad', 'danificada', 'quebrada', 'avariada']):
            support_score += 3

        # Regex for UUID/ID extraction (potential order ID reference)
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        has_uuid = bool(re.search(uuid_pattern, text_lower))
        if has_uuid and track_score > 0:
            track_score += 3
        if has_uuid and support_score > 0:
            support_score += 2

        scores = {
            'track_order': (track_score, 0.5 + min(track_score * 0.15, 0.45)),
            'recommend_vehicle': (vehicle_score, 0.5 + min(vehicle_score * 0.15, 0.45)),
            'open_support_ticket': (support_score, 0.5 + min(support_score * 0.15, 0.45)),
        }

        # Select maximum scoring intent
        best_intent = 'general_query'
        best_confidence = 1.0000

        max_score = 0
        for intent, (score, confidence) in scores.items():
            if score > max_score:
                # If track_order and open_support_ticket tie, prefer open_support_ticket
                # when support indicators are present.
                max_score = score
                best_intent = intent
                best_confidence = confidence
            elif score == max_score and max_score > 0:
                if intent == 'open_support_ticket':
                    best_intent = intent

        return best_intent, Decimal(str(round(best_confidence, 4)))

class RAGService:
    """
    RAG (Retrieval-Augmented Generation) query system using local keyword search
    and structured JSON float cosine similarity simulations.
    """
    @staticmethod
    def get_query_embedding(query_text):
        """
        Creates a deterministic high-dimensional vector based on the query tokens.
        Ensures vector logic passes tests consistently.
        """
        tokens = query_text.lower().split()
        vector = [0.0] * 1536
        if not tokens:
            return vector
            
        for i, token in enumerate(tokens):
            h = hashlib.sha256(token.encode('utf-8')).hexdigest()
            # Generate floats from hexadecimal chunks
            for idx in range(16):
                val = int(h[idx*2:idx*2+2], 16) / 255.0
                vector[(idx + i * 7) % 1536] += val
                
        # Normalize
        norm = math.sqrt(sum(v*v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    @staticmethod
    def cosine_similarity(v1, v2):
        if len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 * norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    @staticmethod
    def search(query_text, category=None, top_k=3):
        # 1. Filter documents
        query_filter = Q(status='published')
        if category:
            query_filter &= Q(category=category)

        # 2. Clean query text and extract alphanumeric tokens
        cleaned_query = re.sub(r'[^\w\s]', '', query_text.lower())
        tokens = [t for t in cleaned_query.split() if len(t) > 2]
        scored_docs = []

        # Fetch candidate documents
        if tokens:
            kw_filter = Q()
            for token in tokens:
                kw_filter |= Q(title__icontains=token) | Q(content__icontains=token) | Q(category__icontains=token)
            candidates = KnowledgeDocument.objects.filter(query_filter & kw_filter)
        else:
            candidates = KnowledgeDocument.objects.filter(query_filter)

        # 3. If KnowledgeEmbeddings exist, compute simulated or exact vector similarity
        embeddings = KnowledgeEmbedding.objects.filter(document__in=candidates)
        if embeddings.exists():
            query_vector = RAGService.get_query_embedding(query_text)
            for emb in embeddings:
                sim = RAGService.cosine_similarity(query_vector, emb.embedding_vector)
                # Boost if category or title matches key query terms
                lexical_boost = 0.0
                doc = emb.document
                for token in tokens:
                    if token in doc.title.lower():
                        lexical_boost += 0.05
                    if token in doc.category.lower():
                        lexical_boost += 0.03
                scored_docs.append((doc, sim + lexical_boost))
            
            # Sort by vector similarity descending
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            results = [item[0] for item in scored_docs[:top_k]]
        else:
            # Standard lexical match scoring
            for doc in candidates:
                score = 0.0
                for token in tokens:
                    if token in doc.title.lower():
                        score += 5.0
                    if token in doc.category.lower():
                        score += 3.0
                    if token in doc.content.lower():
                        score += 1.0
                scored_docs.append((doc, score))
            
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            results = [item[0] for item in scored_docs[:top_k]]

        if not results:
            # Hard fallback
            results = list(KnowledgeDocument.objects.filter(status='published')[:top_k])

        return results

class LLMAdapter:
    """
    Abstrac provider layer for AI text generation. Falls back to smart, context-aware 
    pattern-based local templates when LLM_API_KEY is not defined.
    """
    @staticmethod
    def generate_response(prompt, context_docs=None, intent=None, extra_metadata=None):
        api_key = getattr(settings, 'LLM_API_KEY', None)
        if api_key:
            # Placeholder for future live API integrations
            pass

        # Smart Fallback Local Response Engine
        extra_metadata = extra_metadata or {}
        doc_citations = []
        doc_context = ""
        
        if context_docs:
            doc_citations = [f"[{doc.category}: {doc.title}]" for doc in context_docs]
            doc_context = "\n".join([f"Artigo ({doc.title}): {doc.content}" for doc in context_docs])

        # 1. Intent is track_order
        if intent == 'track_order':
            order = extra_metadata.get('order')
            if not order:
                return "Não encontrei nenhuma ordem de frete recente para você rastrear. Poderia informar o ID ou código do frete?"
            
            status_display = order.get_status_display()
            origin = order.origin_address
            dest = order.destination_address
            eta = order.estimated_arrival_time
            eta_str = eta.strftime('%d/%m/%Y às %H:%M') if eta else "não calculada"
            
            lat = extra_metadata.get('latitude')
            lng = extra_metadata.get('longitude')
            speed = extra_metadata.get('speed', '0.00')

            loc_details = ""
            if lat and lng:
                loc_details = f"\n📍 Última coordenada capturada: Latitude: {lat}, Longitude: {lng}.\n⚡ Velocidade atual do veículo: {speed} km/h."
            else:
                loc_details = "\n⚠️ Sem coordenadas recentes de telemetria GPS no momento."

            return (
                f"Consultei o status atualizado do seu frete **{str(order.id)[:8]}...**:\n\n"
                f"📦 **Origem**: {origin}\n"
                f"🏁 **Destino**: {dest}\n"
                f"🚦 **Status Atual**: {status_display}\n"
                f"⏱️ **Previsão de Chegada (ETA)**: {eta_str}\n"
                f"{loc_details}\n\n"
                "Se precisar de mais detalhes ou quiser registrar alguma ocorrência, estou à disposição."
            )

        # 2. Intent is recommend_vehicle
        if intent == 'recommend_vehicle':
            # Check context documents first
            if context_docs:
                doc_text = context_docs[0].content
                citation = doc_citations[0]
                return (
                    f"Com base nas diretrizes operacionais do sistema {citation}:\n\n"
                    f"{doc_text}\n\n"
                    "Espero que esta recomendação ajude a planejar sua operação logística. "
                    "Se precisar de suporte para agendar ou precificar, é só chamar."
                )
            
            # Static rule fallbacks
            prompt_lower = prompt.lower()
            if 'geladeira' in prompt_lower or 'refrigerado' in prompt_lower or 'frio' in prompt_lower:
                return (
                    "Para o transporte de cargas refrigeradas ou eletrodomésticos sensíveis (como geladeiras):\n\n"
                    "🚚 **Veículo Ideal**: Caminhão Baú Refrigerado de porte leve (VUC ou 3/4) para entregas urbanas, ou Truck para médias distâncias.\n"
                    "📦 **Requisitos**: A carga deve estar bem fixada com cintas, mantida na vertical (no caso de geladeiras) e protegida contra umidade.\n\n"
                    "Gostaria que eu fizesse uma simulação de cotação com essas especificações?"
                )
            elif 'soja' in prompt_lower or 'grão' in prompt_lower or 'milho' in prompt_lower:
                return (
                    "Para o transporte de grãos a granel (como soja ou milho):\n\n"
                    "🚚 **Veículo Ideal**: Carreta Graneleira ou Bitrem com carroceria aberta e alta.\n"
                    "📦 **Requisitos**: É obrigatório o uso de lona de proteção resistente e amarração adequada para evitar perdas na pista durante o trajeto.\n\n"
                    "Gostaria que eu fizesse uma simulação de cotação com essas especificações?"
                )
            else:
                return (
                    "Para recomendar o veículo correto, analiso o peso, volume e características da sua carga:\n\n"
                    "• **Cargas Gerais / Frágeis**: Caminhão Baú Fechado (VUC, 3/4 ou Toco).\n"
                    "• **Grãos e Granel**: Carreta Graneleira com lona.\n"
                    "• **Perecíveis**: Baú Refrigerado.\n"
                    "• **Cargas Pesadas / Maquinário**: Prancha ou Grade Baixa.\n\n"
                    "Poderia me dar mais detalhes sobre o peso total (em KG) e tipo de material a ser transportado?"
                )

        # 3. Intent is open_support_ticket
        if intent == 'open_support_ticket':
            ticket = extra_metadata.get('ticket')
            if ticket:
                ticket_id = str(ticket.id)[:8]
                category_display = ticket.get_category_display()
                priority_display = ticket.get_priority_display()
                return (
                    f"🚨 **Ocorrência Registrada com Sucesso!**\n\n"
                    f"Abri um chamado de suporte técnico em nosso portal operacional:\n"
                    f"• 🎫 **ID do Ticket**: #{ticket_id}\n"
                    f"• 📂 **Categoria**: {category_display}\n"
                    f"• ⚡ **Prioridade**: {priority_display}\n"
                    f"• 📝 **Descrição**: {ticket.description}\n\n"
                    f"Nossa equipe de operações e atendimento humano já foi notificada e "
                    f"entrará em contato muito em breve para resolver esta situação."
                )
            
            return (
                "Entendi que você está enfrentando uma dificuldade ou avaria. "
                "Para que eu possa abrir um chamado de suporte preciso de algumas informações:\n"
                "1. Qual o ID do frete relacionado?\n"
                "2. Descreva brevemente o problema (ex: atraso, mercadoria danificada, pagamento).\n\n"
                "Se preferir, posso registrar o chamado imediatamente. Deseja prosseguir?"
            )

        # 4. General query fallback (uses RAG context if found)
        if context_docs:
            citation_str = ", ".join(doc_citations)
            best_doc = context_docs[0]
            return (
                f"Olá! Busquei informações em nossa base de conhecimento oficial {citation_str}:\n\n"
                f"{best_doc.content}\n\n"
                "Espero que tenha esclarecido sua dúvida. Se precisar de mais alguma ajuda operacional, sinta-se à vontade para perguntar."
            )

        return (
            "Olá! Sou o assistente de inteligência artificial do FreteHub.\n\n"
            "Posso lhe ajudar com as seguintes tarefas:\n"
            "📌 **Rastrear fretes ativos** live via GPS e estimar o tempo de chegada (ETA).\n"
            "🚚 **Recomendar veículos e carrocerias** corretas de acordo com a carga (grãos, perecíveis, geladeiras).\n"
            "🎫 **Registrar chamados e tickets de suporte** em caso de atrasos ou avarias.\n\n"
            "Como posso lhe ajudar hoje?"
        )

class AIOrchestrator:
    """
    Main manager for processing chat messages, validating permissions, 
    consulting live telemetry databases, orchestrating support tickets, and archiving histories.
    """
    @staticmethod
    def process_message(user, conversation_id=None, message_text="", channel='web'):
        # 1. Retrieve or create Conversation
        if conversation_id:
            try:
                conversation = AIConversation.objects.get(id=conversation_id, user=user)
            except AIConversation.DoesNotExist:
                conversation = AIConversation.objects.create(user=user, channel=channel)
        else:
            # Fallback to last active or create new
            conversation = AIConversation.objects.filter(user=user, status='active').first()
            if not conversation:
                conversation = AIConversation.objects.create(user=user, channel=channel)

        # Ensure conversation is open
        if conversation.status == 'closed':
            conversation.status = 'active'
            conversation.save(update_fields=['status'])

        # 2. Save User Message
        AIMessage.objects.create(
            conversation=conversation,
            sender='user',
            message_text=message_text
        )

        # 3. Intent Classification
        intent, confidence = IntentClassifier.classify(message_text)

        # 4. Execute Intent Action & Checks
        extra_metadata = {}
        context_docs = []

        if intent == 'track_order':
            # Extract UUID from text
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            uuid_match = re.search(uuid_pattern, message_text.lower())
            
            order = None
            if uuid_match:
                order_id = uuid_match.group(0)
                try:
                    order = FreightOrder.objects.get(id=order_id)
                except FreightOrder.DoesNotExist:
                    pass
            
            # If no order ID is found or matched, fallback to most recent order of user
            if not order:
                order = FreightOrder.objects.filter(Q(customer=user) | Q(driver=user)).first()

            if order:
                # Permission check!
                if order.customer != user and order.driver != user and not user.is_staff:
                    # Safe security message
                    assistant_msg = AIMessage.objects.create(
                        conversation=conversation,
                        sender='assistant',
                        message_text="Desculpe, por questões de segurança e privacidade da LGPD, você não tem autorização para visualizar informações deste frete.",
                        intent=intent,
                        confidence_score=confidence
                    )
                    return assistant_msg
                
                # Fetch live location cache from Redis
                r = RedisTrackingClient.get_client()
                loc_cache = r.get(f"tracking:order:{order.id}:current_location")
                
                extra_metadata['order'] = order
                if loc_cache:
                    try:
                        loc_dict = json.loads(loc_cache)
                        extra_metadata['latitude'] = loc_dict.get('latitude')
                        extra_metadata['longitude'] = loc_dict.get('longitude')
                        extra_metadata['speed'] = loc_dict.get('speed')
                    except Exception:
                        pass
                else:
                    # Fallback database values if Redis is not populated
                    if hasattr(order, 'driver') and order.driver:
                        profile = getattr(order.driver, 'driver_profile', None)
                        if profile and profile.current_latitude:
                            extra_metadata['latitude'] = str(profile.current_latitude)
                            extra_metadata['longitude'] = str(profile.current_longitude)

        elif intent == 'recommend_vehicle':
            # RAG search for logistics rules
            context_docs = RAGService.search(message_text, category="veiculos", top_k=2)
            if not context_docs:
                context_docs = RAGService.search(message_text, top_k=2)

        elif intent == 'open_support_ticket':
            # Find referenced order if possible
            order = FreightOrder.objects.filter(Q(customer=user) | Q(driver=user)).first()
            
            # Match ticket category based on keywords
            category = 'outro'
            text_lower = message_text.lower()
            if 'avaria' in text_lower or 'danificad' in text_lower or 'estragou' in text_lower or 'quebro' in text_lower:
                category = 'carga_danificada'
            elif 'atras' in text_lower or 'demor' in text_lower:
                category = 'atraso'
            elif 'pagament' in text_lower or 'preco' in text_lower or 'preço' in text_lower or 'cobran' in text_lower:
                category = 'pagamento'
            elif 'cancel' in text_lower:
                category = 'cancelamento'
            elif 'diverg' in text_lower or 'peso' in text_lower or 'volum' in text_lower:
                category = 'divergencia_peso'

            # Set priorities
            priority = 'medium'
            if category in ['carga_danificada', 'cancelamento']:
                priority = 'high'
            if 'grave' in text_lower or 'urgente' in text_lower or 'roubo' in text_lower or 'emergencia' in text_lower:
                priority = 'critical'

            # Create ticket
            ticket = SupportTicket.objects.create(
                user=user,
                freight_order=order,
                category=category,
                priority=priority,
                status='open',
                description=f"Abertura automática via Assistente de IA: {message_text[:200]}...",
                created_from='ai'
            )
            extra_metadata['ticket'] = ticket

            # Register AIAction
            AIAction.objects.create(
                conversation=conversation,
                user=user,
                action_type='abrir_chamado_suporte',
                target_entity='SupportTicket',
                target_id=str(ticket.id),
                status='executed',
                requires_confirmation=False,
                confirmed_at=timezone.now()
            )

        else:
            # General query with standard RAG lookup
            context_docs = RAGService.search(message_text, top_k=2)

        # 5. Generate final response content via LLM Adapter fallback
        response_text = LLMAdapter.generate_response(
            prompt=message_text,
            context_docs=context_docs,
            intent=intent,
            extra_metadata=extra_metadata
        )

        # 6. Save Assistant Response Message
        assistant_msg = AIMessage.objects.create(
            conversation=conversation,
            sender='assistant',
            message_text=response_text,
            intent=intent,
            confidence_score=confidence,
            metadata={
                'citations': [doc.title for doc in context_docs] if context_docs else [],
                'action_triggered': intent if intent in ['track_order', 'open_support_ticket'] else None
            }
        )

        return assistant_msg
