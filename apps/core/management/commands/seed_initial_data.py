from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.companies.models import CompanyProfile, CarrierCompany
from apps.audit.services import create_audit_log

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds initial database records for FreteHub (Module 1 users and profiles)"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando o semeio de dados (Seed Inicial)...")

        # 1. Admin
        admin_email = "admin@fretehub.com"
        if not User.objects.filter(email=admin_email).exists():
            admin = User.objects.create_superuser(
                email=admin_email,
                password="AdminPassword123",
                name="Administrador do Sistema",
                phone="(11) 99999-1111",
                document_type="CPF",
                document_number="11111111111"
            )
            create_audit_log(admin, "Seed - Criação de Superusuário", "User", admin.id)
            self.stdout.write(self.style.SUCCESS(f"Superusuário criado: {admin_email}"))
        else:
            self.stdout.write(f"Usuário {admin_email} já existe.")

        # 2. Cliente PF
        pf_email = "pf_client@fretehub.com"
        if not User.objects.filter(email=pf_email).exists():
            pf = User.objects.create_user(
                email=pf_email,
                password="ClientPassword123",
                name="Roberto Silva (PF)",
                phone="(11) 98888-2222",
                document_type="CPF",
                document_number="22222222222",
                user_type="PF",
                is_verified=True
            )
            create_audit_log(pf, "Seed - Criação de Usuário PF", "User", pf.id)
            self.stdout.write(self.style.SUCCESS(f"Cliente PF criado: {pf_email}"))

        # 3. Cliente PJ
        pj_email = "pj_client@fretehub.com"
        if not User.objects.filter(email=pj_email).exists():
            pj = User.objects.create_user(
                email=pj_email,
                password="ClientPassword123",
                name="Empresa Logística Alfa LTDA (PJ)",
                phone="(11) 97777-3333",
                document_type="CNPJ",
                document_number="33333333000133",
                user_type="PJ",
                is_verified=True
            )
            create_audit_log(pj, "Seed - Criação de Usuário PJ", "User", pj.id)

            # Company profile creation
            profile = CompanyProfile.objects.create(
                user=pj,
                legal_name="Logística Alfa LTDA",
                trade_name="Alfa Log",
                cnpj="33333333000133",
                state_registration="123456789",
                responsible_name="Roberto Silveira",
                responsible_phone="(11) 97777-3333",
                billing_address="Av. Paulista, 1000 - Bela Vista, São Paulo - SP",
                operational_address="Av. das Nações Unidas, 4500 - Pinheiros, São Paulo - SP",
                status="approved"
            )
            create_audit_log(pj, "Seed - Criação de Perfil PJ", "CompanyProfile", profile.id)
            self.stdout.write(self.style.SUCCESS(f"Cliente PJ e perfil criados: {pj_email}"))

        # 4. Motorista
        driver_email = "driver@fretehub.com"
        if not User.objects.filter(email=driver_email).exists():
            driver = User.objects.create_user(
                email=driver_email,
                password="DriverPassword123",
                name="Carlos Souza (Motorista)",
                phone="(11) 96666-4444",
                document_type="CPF",
                document_number="44444444444",
                user_type="DRIVER",
                is_verified=True
            )
            create_audit_log(driver, "Seed - Criação de Usuário Motorista", "User", driver.id)
            self.stdout.write(self.style.SUCCESS(f"Motorista criado: {driver_email}"))

        # 5. Transportadora
        carrier_email = "carrier@fretehub.com"
        if not User.objects.filter(email=carrier_email).exists():
            carrier = User.objects.create_user(
                email=carrier_email,
                password="CarrierPassword123",
                name="Transportes Rápido Brasil (Transportadora)",
                phone="(11) 95555-5555",
                document_type="CNPJ",
                document_number="55555555000155",
                user_type="CARRIER",
                is_verified=True
            )
            create_audit_log(carrier, "Seed - Criação de Usuário Transportadora", "User", carrier.id)

            # Carrier profile creation
            carrier_company = CarrierCompany.objects.create(
                owner_user=carrier,
                legal_name="Transportes Rápido Brasil LTDA",
                trade_name="Rápido Brasil",
                cnpj="55555555000155",
                state_registration="987654321",
                responsible_name="Claudio Mello",
                responsible_phone="(11) 95555-5555",
                billing_address="Rodovia Anhanguera, KM 15 - Jundiaí - SP",
                operational_address="Rodovia Anhanguera, KM 15 - Jundiaí - SP",
                status="approved"
            )
            create_audit_log(carrier, "Seed - Criação de Perfil Transportadora", "CarrierCompany", carrier_company.id)
            self.stdout.write(self.style.SUCCESS(f"Transportadora e perfil criados: {carrier_email}"))

        # 6. Suporte
        support_email = "support@fretehub.com"
        if not User.objects.filter(email=support_email).exists():
            support = User.objects.create_user(
                email=support_email,
                password="OperatorPassword123",
                name="Suporte Operacional",
                phone="(11) 94444-6666",
                document_type="CPF",
                document_number="66666666666",
                user_type="SUPPORT",
                is_verified=True,
                is_staff=True
            )
            create_audit_log(support, "Seed - Criação de Operador de Suporte", "User", support.id)
            self.stdout.write(self.style.SUCCESS(f"Operador de Suporte criado: {support_email}"))

        # 7. Financeiro
        finance_email = "finance@fretehub.com"
        if not User.objects.filter(email=finance_email).exists():
            finance = User.objects.create_user(
                email=finance_email,
                password="OperatorPassword123",
                name="Financeiro Operacional",
                phone="(11) 93333-7777",
                document_type="CPF",
                document_number="77777777777",
                user_type="FINANCE",
                is_verified=True,
                is_staff=True
            )
            create_audit_log(finance, "Seed - Criação de Operador Financeiro", "User", finance.id)
            self.stdout.write(self.style.SUCCESS(f"Operador Financeiro criado: {finance_email}"))

        # 8. Logístico
        logistics_email = "logistics@fretehub.com"
        if not User.objects.filter(email=logistics_email).exists():
            logistics = User.objects.create_user(
                email=logistics_email,
                password="OperatorPassword123",
                name="Logístico Operacional",
                phone="(11) 92222-8888",
                document_type="CPF",
                document_number="88888888888",
                user_type="LOGISTICS",
                is_verified=True,
                is_staff=True
            )
            create_audit_log(logistics, "Seed - Criação de Operador Logístico", "User", logistics.id)
            self.stdout.write(self.style.SUCCESS(f"Operador Logístico criado: {logistics_email}"))

        # === MODULE 2 SEEDING ===
        self.stdout.write("Semeando dados do Módulo 2 (CargoTypes, DriverProfile, Vehicles, Documents)...")

        cargo_types_data = [
            {
                "name": "Geladeira",
                "category": "EQUIPMENTS",
                "slug": "geladeira",
                "description": "Refrigeradores e freezers domésticos ou comerciais.",
                "rule": {
                    "recommended_vehicle_types": ["SMALL_UTILITY", "PICKUP", "FIORINO", "VAN", "LIGHT_TRUCK"],
                    "required_body_types": ["BOX", "SIDER"],
                    "requires_covered_vehicle": True,
                    "requires_helper_recommended": True,
                    "requires_lashing": True,
                    "handling_instructions": "Geladeiras devem ser transportadas estritamente em pé para evitar que o óleo suba ao compressor."
                }
            },
            {
                "name": "Fogão",
                "category": "EQUIPMENTS",
                "slug": "fogao",
                "description": "Fogões, cooktops e fornos.",
                "rule": {
                    "recommended_vehicle_types": ["SMALL_UTILITY", "PICKUP", "FIORINO", "VAN"],
                    "required_body_types": ["BOX", "OPEN"],
                    "requires_covered_vehicle": True,
                    "requires_lashing": True,
                    "handling_instructions": "Fixar os queimadores e tampas de vidro. Exige proteção completa contra umidade/chuva."
                }
            },
            {
                "name": "Móveis",
                "category": "EQUIPMENTS",
                "slug": "moveis",
                "description": "Mesas, cadeiras, sofás, guarda-roupas e armários.",
                "rule": {
                    "recommended_vehicle_types": ["LIGHT_TRUCK", "MEDIUM_TRUCK", "BOX_TRUCK"],
                    "required_body_types": ["BOX", "SIDER"],
                    "requires_covered_vehicle": True,
                    "requires_helper_recommended": True,
                    "requires_lashing": True,
                    "handling_instructions": "Evitar contato direto com assoalho áspero. Utilizar mantas de proteção contra impactos."
                }
            },
            {
                "name": "Soja",
                "category": "DRY_GRAINS",
                "slug": "soja",
                "description": "Grãos de soja a granel.",
                "rule": {
                    "recommended_vehicle_types": ["GRAIN_TRUCK", "GRAIN_TRAILER", "GRAIN_BITREM", "GRAIN_RODOTREM"],
                    "required_body_types": ["GRAIN"],
                    "requires_grain_body": True,
                    "requires_tarp": True,
                    "requires_invoice": True,
                    "requires_weighing": True,
                    "handling_instructions": "Carga agrícola a granel: Exige proteção contra umidade por lona, nota fiscal, romaneio e pesagem inicial/final."
                }
            },
            {
                "name": "Milho",
                "category": "DRY_GRAINS",
                "slug": "milho",
                "description": "Grãos de milho a granel.",
                "rule": {
                    "recommended_vehicle_types": ["GRAIN_TRUCK", "GRAIN_TRAILER", "GRAIN_BITREM", "GRAIN_RODOTREM"],
                    "required_body_types": ["GRAIN"],
                    "requires_grain_body": True,
                    "requires_tarp": True,
                    "requires_invoice": True,
                    "requires_weighing": True,
                    "handling_instructions": "Carga agrícola a granel: Exige proteção contra umidade por lona, nota fiscal, romaneio e pesagem inicial/final."
                }
            }
        ]

        import datetime
        from django.core.files.base import ContentFile
        from apps.drivers.models import DriverProfile
        from apps.vehicles.models import Vehicle
        from apps.cargo.models import CargoType, CargoRule
        from apps.documents.models import Document

        for c_data in cargo_types_data:
            c_type, created = CargoType.objects.get_or_create(
                slug=c_data["slug"],
                defaults={
                    "name": c_data["name"],
                    "category": c_data["category"],
                    "description": c_data["description"],
                    "is_active": True
                }
            )
            if created:
                rule_data = c_data["rule"]
                CargoRule.objects.create(
                    cargo_type=c_type,
                    recommended_vehicle_types=rule_data.get("recommended_vehicle_types", []),
                    required_body_types=rule_data.get("required_body_types", []),
                    requires_covered_vehicle=rule_data.get("requires_covered_vehicle", False),
                    requires_grain_body=rule_data.get("requires_grain_body", False),
                    requires_helper_recommended=rule_data.get("requires_helper_recommended", False),
                    requires_insurance_recommended=rule_data.get("requires_insurance_recommended", False),
                    requires_lashing=rule_data.get("requires_lashing", False),
                    requires_tarp=rule_data.get("requires_tarp", False),
                    requires_invoice=rule_data.get("requires_invoice", False),
                    requires_weighing=rule_data.get("requires_weighing", False),
                    handling_instructions=rule_data.get("handling_instructions", "")
                )
                self.stdout.write(self.style.SUCCESS(f"CargoType e Regras criados: {c_data['name']}"))

        # Seeding Driver Profile for Carlos Souza
        carlos = User.objects.filter(email=driver_email).first()
        if carlos:
            driver_profile, d_created = DriverProfile.objects.get_or_create(
                user=carlos,
                defaults={
                    "cnh_number": "12345678900",
                    "cnh_category": "AD",
                    "cnh_expiration_date": datetime.date(2028, 12, 31),
                    "status": "approved",
                    "accepts_equipment": True,
                    "accepts_dry_grains": True,
                    "is_online": True,
                    "pix_key": "12345678900"
                }
            )
            if d_created:
                self.stdout.write(self.style.SUCCESS("Perfil de Motorista criado para Carlos Souza."))

                # Create CNH Document
                cnh_file = ContentFile(b"carlos_cnh_pdf_mock_content", name="carlos_cnh.pdf")
                Document.objects.create(
                    owner=carlos,
                    document_type="CNH",
                    file=cnh_file,
                    status="approved",
                    reviewed_at=datetime.datetime.now(),
                    reviewed_by=User.objects.filter(is_superuser=True).first()
                )
                self.stdout.write(self.style.SUCCESS("Documento CNH criado e aprovado para Carlos Souza."))

                # Create Vehicle
                vehicle, v_created = Vehicle.objects.get_or_create(
                    owner_driver=carlos,
                    plate="ABC-1234",
                    defaults={
                        "renavam": "12345678901",
                        "brand": "Volvo",
                        "model": "FH 540",
                        "year": 2020,
                        "vehicle_type": "GRAIN_TRUCK",
                        "body_type": "GRAIN",
                        "max_weight_kg": 14000.00,
                        "max_volume_m3": 45.00,
                        "allowed_cargo_types": ["soja", "milho"],
                        "has_insurance": True,
                        "insurance_policy_number": "INS-999888",
                        "status": "approved"
                    }
                )
                if v_created:
                    self.stdout.write(self.style.SUCCESS("Veículo graneleiro Volvo FH 540 criado e aprovado para Carlos Souza."))
                    
                    # Create CRLV Document for Vehicle
                    crlv_file = ContentFile(b"carlos_crlv_pdf_mock_content", name="carlos_crlv.pdf")
                    Document.objects.create(
                        owner=carlos,
                        document_type="CRLV",
                        file=crlv_file,
                        status="approved",
                        reviewed_at=datetime.datetime.now(),
                        reviewed_by=User.objects.filter(is_superuser=True).first()
                    )
                    self.stdout.write(self.style.SUCCESS("Documento CRLV criado e aprovado para Carlos Souza."))

        # === MODULE 3 SEEDING ===
        self.stdout.write("Iniciando o semeio de dados do Módulo 3...")
        
        pj_user = User.objects.filter(email=pj_email).first()
        driver_user = User.objects.filter(email=driver_email).first()
        
        if pj_user and driver_user:
            from decimal import Decimal
            from apps.freight.services import FreightService
            from apps.payments.services import PaymentService
            
            # Seed 1: Completed Freight (Geladeira)
            self.stdout.write("Semeando Frete 1: Geladeira (Concluído)...")
            items_data_fridge = [{
                "cargo_type_slug": "geladeira",
                "description": "Geladeira Brastemp Duplex Retro",
                "estimated_weight_kg": 85.00,
                "estimated_volume_m3": 1.20,
                "quantity": 1,
                "is_fragile": True
            }]
            
            fridge_order = FreightService.create_freight_order(
                customer=pj_user,
                origin_address="Rua Pamplona, 1000 - Jardim Paulista, São Paulo - SP",
                origin_latitude=Decimal("-23.565820"),
                origin_longitude=Decimal("-46.658308"),
                destination_address="Av. Paulista, 1500 - Bela Vista, São Paulo - SP",
                destination_latitude=Decimal("-23.563020"),
                destination_longitude=Decimal("-46.654308"),
                cargo_category="EQUIPMENTS",
                cargo_description="Entrega rápida de eletrodoméstico",
                items_data=items_data_fridge
            )
            
            # Confirm payment
            payment = fridge_order.payments.first()
            if payment:
                PaymentService.simulate_payment_confirmation(payment)
            
            # Accept order
            FreightService.accept_order(fridge_order, driver_user)
            
            # Transition to completed
            FreightService.arrived_origin(fridge_order)
            FreightService.collect_cargo(fridge_order)
            FreightService.start_transit(fridge_order)
            FreightService.arrived_destination(fridge_order)
            FreightService.deliver_cargo(fridge_order)
            FreightService.complete_order(fridge_order)
            
            self.stdout.write(self.style.SUCCESS("Frete de Geladeira (Concluído) semeado com sucesso."))
            
            # Seed 2: Active Freight (Soja)
            self.stdout.write("Semeando Frete 2: Soja (Aguardando Motorista)...")
            items_data_soja = [{
                "cargo_type_slug": "soja",
                "description": "Carga de Soja Agrícola Fina",
                "estimated_weight_kg": 12000.00,
                "estimated_volume_m3": 38.00,
                "quantity": 1,
                "is_fragile": False
            }]
            
            soja_order = FreightService.create_freight_order(
                customer=pj_user,
                origin_address="Fazenda Boa Vista, Km 45, Rondonópolis - MT",
                origin_latitude=Decimal("-16.467800"),
                origin_longitude=Decimal("-54.638500"),
                destination_address="Porto de Paranaguá, Paranaguá - PR",
                destination_latitude=Decimal("-25.502600"),
                destination_longitude=Decimal("-48.509800"),
                cargo_category="DRY_GRAINS",
                cargo_description="Frete agrícola intermunicipal de grãos",
                items_data=items_data_soja
            )
            
            # Confirm payment
            soja_payment = soja_order.payments.first()
            if soja_payment:
                PaymentService.simulate_payment_confirmation(soja_payment)
                
            self.stdout.write(self.style.SUCCESS("Frete de Soja (Aguardando Motorista) semeado com sucesso."))

        self.stdout.write(self.style.SUCCESS("Dados iniciais semeados com sucesso!"))
