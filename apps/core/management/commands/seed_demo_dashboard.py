import random
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.commercial.models import InvestorLead
from apps.freight.models import FreightOrder
from apps.payments.models import Payment
from apps.drivers.models import DriverProfile
from apps.vehicles.models import Vehicle

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds database with a robust dataset for commercial and executive dashboard demonstration."

    def handle(self, *args, **options):
        self.stdout.write("Semeando dados estatísticos e comerciais de demonstração...")

        # 1. Ensure core users exist
        customer = User.objects.filter(user_type='PJ').first()
        if not customer:
            customer = User.objects.filter(user_type='PF').first()
        if not customer:
            customer = User.objects.create_user(
                email="democlient@fretehub.com",
                password="DemoPassword123",
                name="Embarcadora Demo S/A",
                user_type="PJ",
                is_verified=True
            )
            self.stdout.write("Criado cliente PJ de demonstração.")

        driver = User.objects.filter(user_type='DRIVER').first()
        if not driver:
            driver = User.objects.create_user(
                email="demodriver@fretehub.com",
                password="DemoPassword123",
                name="Alexandre Santos (Freteiro)",
                user_type="DRIVER",
                is_verified=True
            )
            self.stdout.write("Criado motorista de demonstração.")

        # Ensure vehicle exists for driver
        vehicle = Vehicle.objects.filter(owner_driver=driver).first()
        if not vehicle:
            # Check if there is any vehicle or create one
            vehicle = Vehicle.objects.first()
            if not vehicle:
                vehicle = Vehicle.objects.create(
                    plate="HUB9D99",
                    brand="Scania",
                    model="R450",
                    year=2021,
                    vehicle_type="caminhao",
                    body_type="graneleira",
                    max_weight_kg=32000,
                    max_volume_m3=80,
                    status="approved"
                )

        # 2. Seed Investor Leads
        leads_data = [
            {"name": "Marcelo Abreu", "email": "marcelo@vclogistics.com", "company": "VC Logistics Partner", "profile_type": "investor", "estimated_interest_level": "strategic", "status": "converted", "notes": "Contrato estratégico fechado de R$ 2M."},
            {"name": "Juliana Ferraz", "email": "juliana@agrovale.com", "company": "Cooperativa AgroVale", "profile_type": "shipper", "estimated_interest_level": "high", "status": "negotiating", "notes": "Interesse em escoamento de grãos safra 2026."},
            {"name": "Claudio Pires", "email": "claudio@sulbrasildist.com", "company": "Sul Brasil Distribuidora", "profile_type": "shipper", "estimated_interest_level": "medium", "status": "contacted", "notes": "Enviada tabela de preços para eletrodomésticos."},
            {"name": "Eduarda Lima", "email": "eduarda@capitalgrowth.com", "company": "Growth Venture Capital", "profile_type": "investor", "estimated_interest_level": "strategic", "status": "meeting_scheduled", "notes": "Reunião de avaliação de take-rate de 15% agendada."},
            {"name": "Renato Rossi", "email": "renato@rossitransporte.com.br", "company": "Rossi Cargas Especiais", "profile_type": "carrier", "estimated_interest_level": "high", "status": "converted", "notes": "Integrado via API com 15 carretas graneleiras."},
            {"name": "Carla Mendes", "email": "carla@revistalog.com", "company": "Logística & Negócios", "profile_type": "press", "estimated_interest_level": "low", "status": "new", "notes": "Solicitação de release institucional sobre o rebranding FreteHub."},
            {"name": "Gustavo Diniz", "email": "gustavo@dinizgraos.com", "company": "Diniz Cerealista", "profile_type": "shipper", "estimated_interest_level": "medium", "status": "lost", "notes": "Sem volume mínimo para a rota atual."},
        ]

        leads_seeded = 0
        for data in leads_data:
            if not InvestorLead.objects.filter(email=data["email"]).exists():
                InvestorLead.objects.create(**data)
                leads_seeded += 1

        self.stdout.write(self.style.SUCCESS(f"Semeados {leads_seeded} novos leads comerciais/investidores."))

        # 3. Seed Freight Orders and Payments
        cargo_items = [
            {"category": "equipamentos", "desc": "Geladeira Duplex Continental e fogões", "weight": 450, "vol": 4.5, "price": 380.00, "vehicle": "Van"},
            {"category": "graos", "desc": "Soja a granel limpa", "weight": 28000, "vol": 72.0, "price": 2850.00, "vehicle": "Carreta Graneleira"},
            {"category": "moveis", "desc": "Mudança residencial de alto padrão", "weight": 1800, "vol": 25.0, "price": 1450.00, "weight_kg": 1800, "price": 1450.00, "vehicle": "Caminhão Médio (Toco)"},
            {"category": "graos", "desc": "Milho seco ensacado", "weight": 14000, "vol": 38.0, "price": 1850.00, "vehicle": "Caminhão Graneleiro"},
            {"category": "equipamentos", "desc": "Motores elétricos industriais", "weight": 3500, "vol": 8.0, "price": 1200.00, "vehicle": "Caminhão Pequeno (3/4)"},
        ]

        freights_seeded = 0
        payments_seeded = 0

        for idx, item in enumerate(cargo_items):
            # Create unique tracking identifier or sequence
            order = FreightOrder.objects.create(
                customer=customer,
                driver=driver,
                vehicle=vehicle,
                origin_address="Cuiabá - MT",
                origin_latitude=Decimal("-15.596"),
                origin_longitude=Decimal("-56.096"),
                destination_address="Rondonópolis - MT",
                destination_latitude=Decimal("-16.470"),
                destination_longitude=Decimal("-54.630"),
                cargo_category=item["category"],
                cargo_description=item["desc"],
                estimated_weight_kg=Decimal(str(item.get("weight") or 500)),
                estimated_volume_m3=Decimal(str(item["vol"])),
                required_vehicle_type=item["vehicle"],
                required_body_type="Qualquer",
                estimated_distance_km=Decimal("210.00"),
                estimated_duration_minutes=180,
                estimated_price=Decimal(str(item["price"])),
                final_price=Decimal(str(item["price"])),
                status="completed",
                delivered_at=timezone.now() - timezone.timedelta(days=random.randint(1, 15))
            )
            freights_seeded += 1

            # Create Paid Payment for Completed Freight
            amount = order.final_price
            fee = amount * Decimal("0.15") # 15% platform take-rate
            driver_payout = amount * Decimal("0.85") # 85% motorista

            Payment.objects.create(
                freight_order=order,
                payer=customer,
                driver=driver,
                amount=amount,
                platform_fee=fee,
                driver_amount=driver_payout,
                status="paid",
                payment_method=random.choice(["pix", "card", "invoice"]),
                transaction_id=f"tx_{uuid.uuid4().hex[:12]}",
                paid_at=order.delivered_at
            )
            payments_seeded += 1

        self.stdout.write(self.style.SUCCESS(f"Semeados {freights_seeded} fretes históricos de demonstração."))
        self.stdout.write(self.style.SUCCESS(f"Semeados {payments_seeded} pagamentos associados (take-rate 15%)."))
        self.stdout.write(self.style.SUCCESS("Banco semeado com sucesso para demonstração comercial FreteHub!"))
