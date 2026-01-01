"""
Management command para criar grupos padrão do Django.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Cria grupos padrão do sistema com permissões básicas'

    def handle(self, *args, **options):
        groups_config = {
            'Tenant Admin': {
                'description': 'Administrador do tenant com todas as permissões',
                'permissions': ['add', 'change', 'delete', 'view'],
            },
            'Manager': {
                'description': 'Gerente com permissões de criar, editar e visualizar',
                'permissions': ['add', 'change', 'view'],
            },
            'Editor': {
                'description': 'Editor de conteúdo público',
                'permissions': ['add', 'change', 'view'],
            },
            'Viewer': {
                'description': 'Visualizador com apenas permissão de leitura',
                'permissions': ['view'],
            },
            'Agent': {
                'description': 'Corretor com permissões para gerenciar próprios imóveis e leads',
                'permissions': ['add', 'change', 'view'],
            },
        }
        
        created_count = 0
        updated_count = 0
        
        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Grupo "{group_name}" criado')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'→ Grupo "{group_name}" já existe')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumo: {created_count} grupos criados, {updated_count} grupos já existiam'
            )
        )



