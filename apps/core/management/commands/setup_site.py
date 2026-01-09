"""
Comando para configurar o Site do Django (necessário para allauth)
"""
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Configura o Site do Django com o domínio correto"

    def handle(self, *args, **options):
        """Configura o Site ID 1 com o domínio correto"""
        try:
            site = Site.objects.get(id=settings.SITE_ID)
            base_domain = getattr(settings, "BASE_DOMAIN", "propzy.com.br")

            if site.domain != base_domain:
                site.domain = base_domain
                site.name = "Propzy"
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Site atualizado: {site.domain} ({site.name})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Site já está configurado corretamente: {site.domain}"
                    )
                )
        except Site.DoesNotExist:
            # Criar site se não existir
            base_domain = getattr(settings, "BASE_DOMAIN", "propzy.com.br")
            site = Site.objects.create(
                id=settings.SITE_ID,
                domain=base_domain,
                name="Propzy"
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Site criado: {site.domain} ({site.name})"
                )
            )



