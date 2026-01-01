"""
Management command customizado para criar superusuário com tenant.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria um superusuário com tenant'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email do superusuário',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha do superusuário',
        )
        parser.add_argument(
            '--tenant',
            type=str,
            help='Slug do tenant (ou será criado um tenant padrão)',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        password = options.get('password')
        tenant_slug = options.get('tenant')

        # Criar ou obter tenant
        if tenant_slug:
            try:
                tenant = Tenant.objects.get(slug=tenant_slug)
            except Tenant.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Tenant com slug "{tenant_slug}" não encontrado.')
                )
                return
        else:
            # Criar tenant padrão se não existir
            tenant, created = Tenant.objects.get_or_create(
                slug='default',
                defaults={
                    'name': 'Tenant Padrão',
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Tenant padrão criado: {tenant.name}')
                )

        # Solicitar email se não fornecido
        if not email:
            email = input('Email: ')

        # Verificar se usuário já existe
        if User.objects.filter(email=email, tenant=tenant).exists():
            self.stdout.write(
                self.style.ERROR(f'Usuário com email "{email}" já existe neste tenant.')
            )
            return

        # Solicitar senha se não fornecida
        if not password:
            password = input('Password: ')
            password_again = input('Password (again): ')
            if password != password_again:
                self.stdout.write(
                    self.style.ERROR('As senhas não coincidem.')
                )
                return

        # Criar superusuário
        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                tenant=tenant,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Superusuário criado com sucesso!\n'
                    f'  Email: {user.email}\n'
                    f'  Tenant: {user.tenant.name}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar superusuário: {e}')
            )



