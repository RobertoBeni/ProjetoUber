from django.core.management.base import BaseCommand
from apps.ai_assistant.models import KnowledgeDocument, KnowledgeEmbedding
from apps.ai_assistant.services import RAGService

class Command(BaseCommand):
    help = "Seeds initial logistics guidelines and vector embeddings for AI RAG chatbot."

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a carga de dados de conhecimento da IA...")

        # Data sets to seed
        articles = [
            {
                "category": "veiculos",
                "title": "Guia de Recomendação de Veículos para Cargas Gerais e Refrigeradas",
                "content": (
                    "Para o transporte de eletrodomésticos sensíveis (como geladeiras, fogões e freezers) ou mercadorias perecíveis, "
                    "é obrigatório o uso de Caminhão Baú Refrigerado ou Caminhão Baú Fechado padrão (porte VUC ou 3/4 para perímetros urbanos, "
                    "e Truck/Carreta para transporte rodoviário interestadual). A arrumação deve manter equipamentos na vertical e utilizar "
                    "cintas de amarração acolchoadas para evitar avarias na lataria ou componentes mecânicos."
                ),
                "version": "1.0",
            },
            {
                "category": "graos",
                "title": "Regulamento Geral de Transporte de Grãos e Granel",
                "content": (
                    "O transporte de grãos a granel (como soja, milho e trigo) deve ser operado exclusivamente por Carretas Graneleiras "
                    "de grade alta ou Bitrens. É expressamente obrigatório o uso de lona de proteção impermeável e perfeitamente amarrada "
                    "em toda a extensão da carroceria, impedindo o derramamento de grãos na via pública sob pena de multa operacional grave "
                    "e retenção da carga."
                ),
                "version": "1.0",
            },
            {
                "category": "lgpd",
                "title": "Termos de Consentimento e Privacidade de Dados de Clientes",
                "content": (
                    "Em conformidade com a LGPD (Lei Geral de Proteção de Dados), o sistema FreteHub audita e criptografa "
                    "dados pessoais de embarcadores e motoristas. O consentimento ativo permite monitoramento de geolocalização por telemetria GPS "
                    "em tempo real de cargas e geração de tempos estimados (ETA) dinâmicos. A qualquer momento, o usuário pode exercer o direito "
                    "de revogação através dos portais de atendimento."
                ),
                "version": "1.0",
            }
        ]

        for art in articles:
            # Create or update document
            doc, created = KnowledgeDocument.objects.update_or_create(
                category=art["category"],
                title=art["title"],
                defaults={
                    "content": art["content"],
                    "version": art["version"],
                    "status": "published"
                }
            )
            
            status_text = "Criado" if created else "Atualizado"
            self.stdout.write(self.style.SUCCESS(f"Documento '{doc.title}' ({status_text})"))

            # Calculate and create embedding vector for RAG similarity search
            vector = RAGService.get_query_embedding(doc.content)
            
            KnowledgeEmbedding.objects.update_or_create(
                document=doc,
                defaults={
                    "embedding_vector": vector,
                    "metadata": {
                        "category": doc.category,
                        "title": doc.title,
                        "length": len(doc.content)
                    }
                }
            )
            self.stdout.write(f"  +-- Embedding gerado com {len(vector)} dimensoes.")

        self.stdout.write(self.style.SUCCESS("Base de dados de conhecimento da IA semeada com sucesso!"))
