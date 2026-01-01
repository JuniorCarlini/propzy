"""
Management command para limpar cache.
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Limpa todo o cache do sistema'

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write(
            self.style.SUCCESS('✓ Cache limpo com sucesso!')
        )



