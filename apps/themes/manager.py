"""
Utilitário para gerenciar temas de landing pages.

Permite escanear, instalar e atualizar temas automaticamente
a partir das pastas em templates/landings/themes/
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.files import File

from .models import Theme


class ThemeManager:
    """Gerenciador de temas de landing pages"""

    def __init__(self):
        """Inicializa o gerenciador"""
        self.themes_dir = Path(settings.BASE_DIR) / "templates" / "landings" / "themes"

    def scan_themes(self) -> list[dict]:
        """
        Escaneia a pasta de temas e retorna lista de temas encontrados.

        Returns:
            Lista de dicionários com configurações dos temas (theme.json)
        """
        if not self.themes_dir.exists():
            return []

        themes = []
        for theme_dir in self.themes_dir.iterdir():
            if theme_dir.is_dir():
                config_file = theme_dir / "theme.json"
                if config_file.exists():
                    try:
                        with open(config_file, encoding="utf-8") as f:
                            config = json.load(f)
                            config["path"] = str(theme_dir)
                            themes.append(config)
                    except (OSError, json.JSONDecodeError) as e:
                        print(f"⚠️  Erro ao ler {config_file}: {e}")

        return themes

    def install_theme(self, slug: str, force_update: bool = False) -> Theme | None:
        """
        Instala ou atualiza um tema no banco de dados baseado no theme.json.

        Args:
            slug: Slug do tema (nome da pasta)
            force_update: Se True, atualiza mesmo se já existir

        Returns:
            Instância de Theme criada/atualizada ou None em caso de erro
        """
        theme_dir = self.themes_dir / slug
        config_file = theme_dir / "theme.json"

        if not config_file.exists():
            raise FileNotFoundError(f"Tema '{slug}' não encontrado em {theme_dir}")

        try:
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Arquivo theme.json inválido para tema '{slug}': {e}")

        # Valida campos obrigatórios
        if "name" not in config:
            raise ValueError(f"Campo 'name' obrigatório no theme.json do tema '{slug}'")

        # Cria ou atualiza o tema
        defaults = {
            "name": config.get("name", slug),
            "description": config.get("description", ""),
            "author": config.get("author", ""),
            "version": config.get("version", "1.0.0"),
            "category": config.get("category", "modern"),
            "default_primary_color": config.get("colors", {}).get("primary", "#007bff"),
            "default_secondary_color": config.get("colors", {}).get("secondary", "#6c757d"),
            "features": config.get("features", []),
            "is_active": True,
        }

        # Se premium está definido no JSON, usa o valor
        if "premium" in config:
            defaults["is_premium"] = config["premium"]

        theme, created = Theme.objects.update_or_create(slug=slug, defaults=defaults)

        # Atualiza screenshot se existir e ainda não tiver sido definido
        screenshot_filename = config.get("screenshot", "preview.jpg")
        screenshot_file = theme_dir / screenshot_filename

        if screenshot_file.exists() and (not theme.screenshot or force_update):
            try:
                with open(screenshot_file, "rb") as f:
                    theme.screenshot.save(f"{slug}_preview.jpg", File(f), save=True)
            except OSError as e:
                print(f"⚠️  Erro ao salvar screenshot do tema '{slug}': {e}")

        action = "instalado" if created else "atualizado"
        print(f"✅ Tema '{config['name']}' ({slug}) {action} com sucesso!")

        return theme

    def install_all_themes(self, force_update: bool = False) -> int:
        """
        Instala todos os temas encontrados na pasta de temas.

        Args:
            force_update: Se True, atualiza temas existentes

        Returns:
            Número de temas instalados com sucesso
        """
        themes = self.scan_themes()

        if not themes:
            print("❌ Nenhum tema encontrado")
            return 0

        print(f"📦 Encontrados {len(themes)} tema(s)")

        installed_count = 0
        for theme_config in themes:
            try:
                self.install_theme(theme_config["slug"], force_update=force_update)
                installed_count += 1
            except Exception as e:
                print(f"❌ Erro ao instalar tema '{theme_config.get('slug', '?')}': {e}")

        return installed_count

    def get_theme_info(self, slug: str) -> dict:
        """
        Retorna informações do tema a partir do theme.json.

        Args:
            slug: Slug do tema

        Returns:
            Dicionário com configurações do tema ou {} se não encontrado
        """
        theme_dir = self.themes_dir / slug
        config_file = theme_dir / "theme.json"

        if not config_file.exists():
            return {}

        try:
            with open(config_file, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def validate_theme(self, slug: str) -> tuple[bool, list[str]]:
        """
        Valida se um tema está corretamente estruturado.

        Args:
            slug: Slug do tema

        Returns:
            Tupla (é_válido, lista_de_erros)
        """
        errors = []
        theme_dir = self.themes_dir / slug

        # Verifica se a pasta existe
        if not theme_dir.exists():
            errors.append(f"Pasta do tema não encontrada: {theme_dir}")
            return False, errors

        # Verifica se theme.json existe
        config_file = theme_dir / "theme.json"
        if not config_file.exists():
            errors.append("Arquivo theme.json não encontrado")
        else:
            # Valida o JSON
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = json.load(f)

                # Valida campos obrigatórios
                required_fields = ["name", "slug"]
                for field in required_fields:
                    if field not in config:
                        errors.append(f"Campo obrigatório ausente no theme.json: {field}")

            except json.JSONDecodeError:
                errors.append("Arquivo theme.json com formato inválido")

        # Verifica se index.html existe
        index_file = theme_dir / "index.html"
        if not index_file.exists():
            errors.append("Arquivo index.html não encontrado")

        return len(errors) == 0, errors


# Instância global do gerenciador
theme_manager = ThemeManager()












