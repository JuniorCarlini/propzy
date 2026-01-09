"""
Management command para gerenciar certificados SSL
"""

from django.core.management.base import BaseCommand, CommandError

from apps.landings.models import LandingPage
from apps.landings.ssl_manager import ssl_manager


class Command(BaseCommand):
    help = "Gerencia certificados SSL para domínios personalizados"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            type=str,
            choices=["generate", "renew", "renew-all", "check", "delete", "list"],
            help="Ação a executar",
        )
        parser.add_argument("--domain", type=str, help="Domínio específico (obrigatório para generate, check, delete)")
        parser.add_argument("--email", type=str, help="Email para notificações do Let's Encrypt")

    def handle(self, *args, **options):
        action = options["action"]
        domain = options.get("domain")
        email = options.get("email")

        if action == "generate":
            self.generate_certificate(domain, email)
        elif action == "renew":
            self.renew_certificate(domain)
        elif action == "renew-all":
            self.renew_all_certificates()
        elif action == "check":
            self.check_certificate(domain)
        elif action == "delete":
            self.delete_certificate(domain)
        elif action == "list":
            self.list_certificates()

    def generate_certificate(self, domain, email):
        """Gera certificado para um domínio"""
        if not domain:
            raise CommandError("--domain é obrigatório para generate")

        self.stdout.write(f"🔐 Gerando certificado para {domain}...")

        # Buscar landing page
        try:
            landing_page = LandingPage.objects.get(custom_domain=domain)
            if not email:
                email = landing_page.owner.email
        except LandingPage.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"⚠️  Landing page não encontrada para {domain}. Continuando..."))

        # Gerar certificado
        success, message = ssl_manager.generate_certificate(domain, email)

        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ {message}"))

            # Atualizar landing page
            try:
                landing_page = LandingPage.objects.get(custom_domain=domain)
                landing_page.ssl_status = "active"
                landing_page.ssl_error = None
                landing_page.save(update_fields=["ssl_status", "ssl_error"])
                self.stdout.write(self.style.SUCCESS("✅ Status atualizado no banco"))
            except LandingPage.DoesNotExist:
                pass
        else:
            self.stdout.write(self.style.ERROR(f"❌ {message}"))

            # Atualizar landing page
            try:
                landing_page = LandingPage.objects.get(custom_domain=domain)
                landing_page.ssl_status = "error"
                landing_page.ssl_error = message
                landing_page.save(update_fields=["ssl_status", "ssl_error"])
            except LandingPage.DoesNotExist:
                pass

    def renew_certificate(self, domain):
        """Renova certificado de um domínio"""
        if not domain:
            raise CommandError("--domain é obrigatório para renew")

        self.stdout.write(f"🔄 Renovando certificado para {domain}...")

        success, message = ssl_manager.renew_certificate(domain)

        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ {message}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ {message}"))

    def renew_all_certificates(self):
        """Renova todos os certificados"""
        self.stdout.write("🔄 Renovando todos os certificados...")

        renewed, errors = ssl_manager.renew_all_certificates()

        self.stdout.write(self.style.SUCCESS(f"✅ Renovação concluída: {renewed} renovados, {errors} erros"))

    def check_certificate(self, domain):
        """Verifica status do certificado de um domínio"""
        if not domain:
            raise CommandError("--domain é obrigatório para check")

        self.stdout.write(f"🔍 Verificando certificado de {domain}...")

        info = ssl_manager.get_certificate_info(domain)

        if info.get("has_certificate"):
            self.stdout.write(self.style.SUCCESS("✅ Certificado encontrado"))
            if "expiry_date" in info:
                self.stdout.write(f"📅 Expira em: {info['expiry_date']}")
        else:
            self.stdout.write(self.style.WARNING("⚠️  Sem certificado"))
            if "error" in info:
                self.stdout.write(self.style.ERROR(f"❌ {info['error']}"))

    def delete_certificate(self, domain):
        """Remove certificado de um domínio"""
        if not domain:
            raise CommandError("--domain é obrigatório para delete")

        self.stdout.write(f"🗑️  Removendo certificado de {domain}...")

        success, message = ssl_manager.delete_certificate(domain)

        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ {message}"))

            # Atualizar landing page
            try:
                landing_page = LandingPage.objects.get(custom_domain=domain)
                landing_page.ssl_status = "none"
                landing_page.ssl_error = None
                landing_page.save(update_fields=["ssl_status", "ssl_error"])
            except LandingPage.DoesNotExist:
                pass
        else:
            self.stdout.write(self.style.ERROR(f"❌ {message}"))

    def list_certificates(self):
        """Lista todas as landing pages com domínios personalizados"""
        self.stdout.write("📋 Landing Pages com Domínios Personalizados:\n")

        landing_pages = LandingPage.objects.filter(custom_domain__isnull=False).exclude(custom_domain="")

        if not landing_pages.exists():
            self.stdout.write(self.style.WARNING("⚠️  Nenhum domínio personalizado encontrado"))
            return

        for lp in landing_pages:
            has_cert = ssl_manager.domain_has_certificate(lp.custom_domain)
            cert_icon = "🔒" if has_cert else "🔓"
            status_icon = {"active": "✅", "generating": "⏳", "error": "❌", "none": "⚪"}.get(lp.ssl_status, "❓")

            self.stdout.write(
                f"{cert_icon} {status_icon} {lp.custom_domain} "
                f"({lp.business_name}) - Status: {lp.get_ssl_status_display()}"
            )

            if lp.ssl_error:
                self.stdout.write(self.style.ERROR(f"   └─ Erro: {lp.ssl_error[:100]}..."))

















