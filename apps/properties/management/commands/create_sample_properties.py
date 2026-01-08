"""
Comando Django para criar imóveis de exemplo.

Uso:
    python manage.py create_sample_properties              # Cria 5 imóveis de exemplo
    python manage.py create_sample_properties --count 10  # Cria 10 imóveis
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

from apps.landings.models import Site
from apps.properties.models import Property


class Command(BaseCommand):
    """Comando para criar imóveis de exemplo"""

    help = "Cria imóveis de exemplo para teste do sistema"

    def add_arguments(self, parser):
        """Adiciona argumentos ao comando"""
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Número de imóveis a criar (padrão: 5)",
        )
        parser.add_argument(
            "--site",
            type=str,
            help="Subdomínio do site (deixe vazio para usar o primeiro disponível)",
        )

    def handle(self, *args, **options):
        """Executa o comando"""
        count = options["count"]
        site_subdomain = options.get("site")

        # Busca ou cria um site
        try:
            if site_subdomain:
                site = Site.objects.get(subdomain=site_subdomain)
            else:
                site = Site.objects.first()
                if not site:
                    self.stdout.write(
                        self.style.ERROR(
                            "Nenhum site encontrado. Crie um site primeiro através do admin ou dashboard."
                        )
                    )
                    return
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Site '{site_subdomain}' não encontrado."))
            return

        self.stdout.write(f"Criando {count} imóveis de exemplo para o site: {site.business_name}")

        # Dados de exemplo
        sample_properties = [
            {
                "title": "Casa Moderna com Piscina - Campo da Água Verde",
                "description": "Excelente casa moderna com 3 quartos, 2 banheiros, sala ampla, cozinha integrada, área gourmet com churrasqueira e piscina. Localizada em bairro nobre, próximo a escolas e comércio.",
                "property_type": "house",
                "category": "urban",
                "transaction_type": "sale",
                "sale_price": Decimal("450000.00"),
                "rent_price": None,
                "bedrooms": 3,
                "bathrooms": 2,
                "garage_spaces": 2,
                "area": Decimal("180.00"),
                "address": "Rua das Flores, 123",
                "neighborhood": "Campo da Água Verde",
                "city": "Canoinhas",
                "state": "SC",
                "zipcode": "89460-000",
                "is_featured": True,
                "is_active": True,
                "order": 1,
            },
            {
                "title": "Apartamento 2 Quartos - Centro",
                "description": "Apartamento bem localizado no centro da cidade, com 2 quartos, 1 banheiro, sala, cozinha e área de serviço. Prédio com portaria e elevador.",
                "property_type": "apartment",
                "category": "urban",
                "transaction_type": "rent",
                "sale_price": None,
                "rent_price": Decimal("1200.00"),
                "bedrooms": 2,
                "bathrooms": 1,
                "garage_spaces": 1,
                "area": Decimal("65.00"),
                "address": "Av. Getúlio Vargas, 456",
                "neighborhood": "Centro",
                "city": "Canoinhas",
                "state": "SC",
                "zipcode": "89460-000",
                "is_featured": False,
                "is_active": True,
                "order": 2,
            },
            {
                "title": "Sala Comercial - Centro Empresarial",
                "description": "Sala comercial em excelente localização, ideal para escritórios ou consultórios. Prédio comercial com estacionamento e fácil acesso.",
                "property_type": "commercial",
                "category": "urban",
                "transaction_type": "both",
                "sale_price": Decimal("280000.00"),
                "rent_price": Decimal("2500.00"),
                "bedrooms": 0,
                "bathrooms": 1,
                "garage_spaces": 2,
                "area": Decimal("85.00"),
                "address": "Rua Comercial, 789",
                "neighborhood": "Centro",
                "city": "Canoinhas",
                "state": "SC",
                "zipcode": "89460-000",
                "is_featured": True,
                "is_active": True,
                "order": 3,
            },
            {
                "title": "Terreno 500m² - Loteamento Residencial",
                "description": "Terreno plano e regularizado em loteamento residencial, com toda documentação em dia. Localização privilegiada, próximo ao centro.",
                "property_type": "land",
                "category": "urban",
                "transaction_type": "sale",
                "sale_price": Decimal("85000.00"),
                "rent_price": None,
                "bedrooms": 0,
                "bathrooms": 0,
                "garage_spaces": 0,
                "area": Decimal("500.00"),
                "address": "Rua Nova Esperança, 321",
                "neighborhood": "Bela Vista",
                "city": "Canoinhas",
                "state": "SC",
                "zipcode": "89460-000",
                "is_featured": False,
                "is_active": True,
                "order": 4,
            },
            {
                "title": "Casa com Chácara - Zona Rural",
                "description": "Casa rústica em chácara de 2 hectares, com 4 quartos, 2 banheiros, área de lazer, pomar e espaço para criação de animais. Ideal para quem busca tranquilidade.",
                "property_type": "farm",
                "category": "rural",
                "transaction_type": "sale",
                "sale_price": Decimal("320000.00"),
                "rent_price": None,
                "bedrooms": 4,
                "bathrooms": 2,
                "garage_spaces": 3,
                "area": Decimal("20000.00"),
                "address": "Estrada Rural, Km 5",
                "neighborhood": "Zona Rural",
                "city": "Canoinhas",
                "state": "SC",
                "zipcode": "89460-000",
                "is_featured": True,
                "is_active": True,
                "order": 5,
            },
            {
                "title": "Apartamento 3 Quartos - Alto Padrão",
                "description": "Apartamento de alto padrão com 3 quartos sendo 1 suíte, 2 banheiros, sala ampla, cozinha planejada, varanda gourmet e 2 vagas de garagem. Prédio com piscina, academia e salão de festas.",
                "property_type": "apartment",
                "category": "urban",
                "transaction_type": "both",
                "sale_price": Decimal("380000.00"),
                "rent_price": Decimal("2500.00"),
                "bedrooms": 3,
                "bathrooms": 2,
                "garage_spaces": 2,
                "area": Decimal("110.00"),
                "address": "Av. Principal, 1000",
                "neighborhood": "Jardim das Flores",
                "city": "Canoinhas",
                "state": "SC",
                "zipcode": "89460-000",
                "is_featured": True,
                "is_active": True,
                "order": 6,
            },
            {
                "title": "Casa Geminada 2 Quartos",
                "description": "Casa geminada em condomínio fechado, com 2 quartos, 1 banheiro, sala, cozinha e área de serviço. Condomínio com portaria, piscina e playground.",
                "property_type": "house",
                "category": "urban",
                "transaction_type": "rent",
                "sale_price": None,
                "rent_price": Decimal("1500.00"),
                "bedrooms": 2,
                "bathrooms": 1,
                "garage_spaces": 1,
                "area": Decimal("75.00"),
                "address": "Rua dos Lírios, 55",
                "neighborhood": "Vila Nova",
                "city": "Canoinhas",
                "state": "SC",
                "zipcode": "89460-000",
                "is_featured": False,
                "is_active": True,
                "order": 7,
            },
            {
                "title": "Loja Comercial - Rua Movimentada",
                "description": "Loja comercial em rua de grande movimento, ideal para diversos tipos de negócios. Localização estratégica com grande fluxo de pessoas.",
                "property_type": "commercial",
                "category": "urban",
                "transaction_type": "rent",
                "sale_price": None,
                "rent_price": Decimal("3500.00"),
                "bedrooms": 0,
                "bathrooms": 1,
                "garage_spaces": 0,
                "area": Decimal("120.00"),
                "address": "Rua do Comércio, 200",
                "neighborhood": "Centro",
                "city": "Canoinhas",
                "state": "SC",
                "zipcode": "89460-000",
                "is_featured": False,
                "is_active": True,
                "order": 8,
            },
        ]

        # Cria uma imagem placeholder simples (1x1 pixel PNG transparente)
        # Nota: O campo main_image é obrigatório, então vamos criar sem imagem primeiro
        # e depois o usuário pode adicionar imagens reais pelo admin

        created_count = 0
        for i, prop_data in enumerate(sample_properties[:count]):
            try:
                # Remove main_image dos dados pois vamos criar sem imagem
                # O campo main_image é obrigatório, então precisamos criar uma imagem mínima
                from PIL import Image
                from io import BytesIO

                # Cria uma imagem PNG simples (800x600, cor cinza claro)
                img = Image.new('RGB', (800, 600), color='#e0e0e0')
                img_buffer = BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)

                placeholder_image = ContentFile(img_buffer.read(), name=f"property_{i+1}_placeholder.png")

                # Cria o imóvel com imagem placeholder
                property_obj = Property.objects.create(
                    site=site,
                    main_image=placeholder_image,
                    **prop_data
                )

                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Criado: {property_obj.title} (ID: {property_obj.id})")
                )
            except ImportError:
                # Se PIL não estiver disponível, tenta criar sem imagem
                self.stdout.write(
                    self.style.WARNING("PIL/Pillow não disponível. Criando imóveis sem imagem...")
                )
                # Remove main_image e tenta criar sem
                prop_data_no_img = {k: v for k, v in prop_data.items() if k != 'main_image'}
                try:
                    property_obj = Property.objects.create(site=site, **prop_data_no_img)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Criado (sem imagem): {property_obj.title} (ID: {property_obj.id})")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Erro ao criar imóvel {i+1}: {e}")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Erro ao criar imóvel {i+1}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Total de {created_count} imóveis criados com sucesso!")
        )

