"""
Comando Django para instalar/atualizar temas automaticamente.

Uso:
    python manage.py install_themes              # Instala todos os temas
    python manage.py install_themes modern       # Instala apenas 'modern'
    python manage.py install_themes --scan       # Apenas lista temas disponíveis
    python manage.py install_themes --force      # Força atualização de todos
"""

from django.core.management.base import BaseCommand

from apps.landings.theme_manager import ThemeManager


class Command(BaseCommand):
    """Comando para instalar temas de landing pages"""

    help = "Instala ou atualiza temas de landing pages a partir de templates/landings/themes/"

    def add_arguments(self, parser):
        """Adiciona argumentos ao comando"""
        parser.add_argument(
            "themes", nargs="*", type=str, help="Slugs dos temas para instalar (deixe vazio para instalar todos)"
        )
        parser.add_argument("--scan", action="store_true", help="Apenas lista os temas disponíveis sem instalar")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Força atualização de temas existentes (incluindo screenshots)",
        )
        parser.add_argument("--validate", action="store_true", help="Valida a estrutura dos temas sem instalar")

    def handle(self, *args, **options):
        """Executa o comando"""
        manager = ThemeManager()

        # Modo: Escanear apenas
        if options["scan"]:
            self._scan_themes(manager)
            return

        # Modo: Validar apenas
        if options["validate"]:
            self._validate_themes(manager, options["themes"])
            return

        # Modo: Instalar
        theme_slugs = options["themes"]
        force_update = options["force"]

        if theme_slugs:
            # Instala temas específicos
            self._install_specific_themes(manager, theme_slugs, force_update)
        else:
            # Instala todos os temas
            self._install_all_themes(manager, force_update)

    def _scan_themes(self, manager: ThemeManager):
        """Lista todos os temas disponíveis"""
        themes = manager.scan_themes()

        if themes:
            self.stdout.write(self.style.SUCCESS(f"\n📦 Encontrados {len(themes)} tema(s):\n"))
            for theme in themes:
                category = theme.get("category", "?")
                version = theme.get("version", "?")
                premium = " [PREMIUM]" if theme.get("premium", False) else ""
                self.stdout.write(f"  • {theme['name']} ({theme['slug']}) - v{version} - {category}{premium}")
                if theme.get("description"):
                    self.stdout.write(f"    {theme['description']}")
            self.stdout.write("")
        else:
            self.stdout.write(self.style.WARNING("\n❌ Nenhum tema encontrado\n"))

    def _validate_themes(self, manager: ThemeManager, theme_slugs: list):
        """Valida a estrutura dos temas"""
        themes_to_validate = theme_slugs if theme_slugs else [t["slug"] for t in manager.scan_themes()]

        if not themes_to_validate:
            self.stdout.write(self.style.WARNING("\n❌ Nenhum tema para validar\n"))
            return

        self.stdout.write(self.style.SUCCESS(f"\n🔍 Validando {len(themes_to_validate)} tema(s):\n"))

        all_valid = True
        for slug in themes_to_validate:
            is_valid, errors = manager.validate_theme(slug)

            if is_valid:
                self.stdout.write(self.style.SUCCESS(f"  ✅ {slug}: OK"))
            else:
                all_valid = False
                self.stdout.write(self.style.ERROR(f"  ❌ {slug}: ERROS ENCONTRADOS"))
                for error in errors:
                    self.stdout.write(f"     - {error}")

        self.stdout.write("")
        if all_valid:
            self.stdout.write(self.style.SUCCESS("✅ Todos os temas são válidos!\n"))
        else:
            self.stdout.write(self.style.ERROR("❌ Alguns temas possuem erros\n"))

    def _install_specific_themes(self, manager: ThemeManager, theme_slugs: list, force_update: bool):
        """Instala temas específicos"""
        self.stdout.write(self.style.SUCCESS(f"\n📦 Instalando {len(theme_slugs)} tema(s):\n"))

        success_count = 0
        for slug in theme_slugs:
            try:
                manager.install_theme(slug, force_update=force_update)
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Erro ao instalar '{slug}': {e}"))

        self.stdout.write("")
        if success_count == len(theme_slugs):
            self.stdout.write(self.style.SUCCESS(f"✅ {success_count} tema(s) instalado(s) com sucesso!\n"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️  {success_count}/{len(theme_slugs)} tema(s) instalado(s)\n"))

    def _install_all_themes(self, manager: ThemeManager, force_update: bool):
        """Instala todos os temas encontrados"""
        self.stdout.write(self.style.SUCCESS("\n📦 Instalando todos os temas encontrados...\n"))

        installed_count = manager.install_all_themes(force_update=force_update)

        self.stdout.write("")
        if installed_count > 0:
            self.stdout.write(self.style.SUCCESS(f"✅ {installed_count} tema(s) instalado(s) com sucesso!\n"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Nenhum tema foi instalado\n"))

















