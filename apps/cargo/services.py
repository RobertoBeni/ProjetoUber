from apps.cargo.models import CargoType, CargoRule

class CargoCompatibilityService:
    """
    Logistics rule engine checking compatibility between cargo requirements
    and vehicle profiles.
    """
    @staticmethod
    def get_recommendation(cargo_slug, weight_kg=0, volume_m3=0, quantity=1, is_fragile=False):
        try:
            # Query standard database records
            cargo_type = CargoType.objects.get(slug=cargo_slug, is_active=True)
            rule = cargo_type.rule
        except Exception:
            # Safe operational fallback if rules are missing
            return {
                "recommended_vehicle_types": ["PICKUP", "LIGHT_TRUCK"],
                "required_body_types": ["BOX", "OPEN"],
                "warnings": ["Regras de compatibilidade padrão aplicadas."],
                "handling_instructions": "Manusear com cuidados gerais de transporte.",
                "requires_helper": False,
                "requires_insurance": False,
                "requires_invoice": False,
                "requires_weighing": False
            }

        warnings = []
        handling_instructions = rule.handling_instructions
        
        # Category/Slug heuristics checks
        if cargo_slug == 'geladeira':
            warnings.append("ATENÇÃO: Geladeiras devem ser transportadas estritamente em pé para evitar que o óleo suba ao compressor.")
        elif cargo_slug == 'fogao':
            warnings.append("Fixar os queimadores e tampas de vidro. Exige proteção completa contra umidade/chuva.")
        elif cargo_slug == 'motor':
            warnings.append("Alerta: Risco de vazamento de fluidos. Utilizar forração absorvente de piso e fixação por travas.")
        elif cargo_slug == 'moveis':
            warnings.append("Evitar contato direto com assoalho áspero. Utilizar mantas de proteção contra impactos.")
        elif cargo_slug == 'pecas':
            warnings.append("Exige acomodação em caixas de proteção ou pallets cintados.")
            
        if cargo_type.category == 'DRY_GRAINS':
            warnings.append("Carga agrícola a granel: Exige proteção contra umidade por lona, nota fiscal, romaneio e pesagem inicial/final.")

        # Determine helper, insurance, invoice, and scale checkups dynamically
        requires_helper = rule.requires_helper_recommended or (weight_kg > 60 or volume_m3 > 1.5 or quantity > 3)
        requires_insurance = rule.requires_insurance_recommended or is_fragile or (weight_kg > 2000)
        requires_invoice = rule.requires_invoice or (cargo_type.category == 'DRY_GRAINS')
        requires_weighing = rule.requires_weighing or (cargo_type.category == 'DRY_GRAINS')

        return {
            "recommended_vehicle_types": rule.recommended_vehicle_types,
            "required_body_types": rule.required_body_types,
            "warnings": warnings,
            "handling_instructions": handling_instructions,
            "requires_helper": requires_helper,
            "requires_insurance": requires_insurance,
            "requires_invoice": requires_invoice,
            "requires_weighing": requires_weighing
        }
