"""
Gerenciador de Certificados SSL para Domínios Personalizados
Gera e renova certificados Let's Encrypt automaticamente
"""

import logging
import subprocess
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


class SSLManager:
    """Gerencia certificados SSL para domínios personalizados"""

    def __init__(self):
        self.certbot_path = "/usr/bin/certbot"
        self.webroot_path = "/var/www/certbot"
        self.nginx_config_path = "/etc/nginx/sites-enabled"
        self.ssl_path = "/etc/letsencrypt/live"

    def ensure_webroot_exists(self):
        """Garante que o diretório webroot existe"""
        Path(self.webroot_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Webroot path verified: {self.webroot_path}")

    def domain_has_certificate(self, domain: str) -> bool:
        """
        Verifica se um domínio já tem certificado válido

        Args:
            domain: Domínio a verificar (ex: dominio-cliente.com.br)

        Returns:
            True se tem certificado, False caso contrário
        """
        cert_path = Path(self.ssl_path) / domain / "fullchain.pem"
        return cert_path.exists()

    def generate_certificate(self, domain: str, email: str = None) -> tuple[bool, str]:
        """
        Gera certificado SSL para um domínio usando Let's Encrypt

        Args:
            domain: Domínio para gerar certificado (ex: dominio-cliente.com.br)
            email: Email para notificações (opcional)

        Returns:
            (sucesso, mensagem)
        """
        try:
            # Garantir que webroot existe
            self.ensure_webroot_exists()

            # Email padrão se não fornecido
            if not email:
                email = settings.DEFAULT_FROM_EMAIL

            # Verificar se já tem certificado
            if self.domain_has_certificate(domain):
                logger.info(f"Certificado já existe para {domain}")
                return True, f"Certificado já existe para {domain}"

            # Comando certbot
            cmd = [
                self.certbot_path,
                "certonly",
                "--webroot",
                "-w",
                self.webroot_path,
                "-d",
                domain,
                "-d",
                f"www.{domain}",  # Incluir www também
                "--non-interactive",
                "--agree-tos",
                "--email",
                email,
                "--deploy-hook",
                "nginx -s reload",  # Recarregar NGINX após sucesso
            ]

            logger.info(f"Gerando certificado para {domain}...")

            # Executar certbot
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # Timeout de 2 minutos
            )

            if result.returncode == 0:
                logger.info(f"✅ Certificado gerado com sucesso para {domain}")
                return True, f"Certificado gerado com sucesso para {domain}"
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"❌ Erro ao gerar certificado para {domain}: {error_msg}")
                return False, f"Erro ao gerar certificado: {error_msg}"

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout ao gerar certificado para {domain}")
            return False, "Timeout ao gerar certificado (mais de 2 minutos)"

        except Exception as e:
            logger.error(f"❌ Exceção ao gerar certificado para {domain}: {str(e)}")
            return False, f"Erro inesperado: {str(e)}"

    def renew_certificate(self, domain: str) -> tuple[bool, str]:
        """
        Renova certificado SSL de um domínio

        Args:
            domain: Domínio para renovar certificado

        Returns:
            (sucesso, mensagem)
        """
        try:
            if not self.domain_has_certificate(domain):
                return False, f"Domínio {domain} não tem certificado para renovar"

            cmd = [self.certbot_path, "renew", "--cert-name", domain, "--deploy-hook", "nginx -s reload"]

            logger.info(f"Renovando certificado para {domain}...")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                logger.info(f"✅ Certificado renovado para {domain}")
                return True, "Certificado renovado com sucesso"
            else:
                # Certbot retorna código 0 mesmo se não precisa renovar
                if "not yet due for renewal" in result.stdout:
                    logger.info(f"Certificado de {domain} ainda não precisa renovar")
                    return True, "Certificado ainda válido, não precisa renovar"

                error_msg = result.stderr or result.stdout
                logger.error(f"❌ Erro ao renovar certificado de {domain}: {error_msg}")
                return False, f"Erro ao renovar: {error_msg}"

        except Exception as e:
            logger.error(f"❌ Exceção ao renovar certificado de {domain}: {str(e)}")
            return False, f"Erro inesperado: {str(e)}"

    def renew_all_certificates(self) -> tuple[int, int]:
        """
        Renova todos os certificados que estão próximos do vencimento

        Returns:
            (total_renovados, total_erros)
        """
        try:
            cmd = [self.certbot_path, "renew", "--deploy-hook", "nginx -s reload"]

            logger.info("Renovando todos os certificados...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos para renovar todos
            )

            # Analisar resultado
            output = result.stdout
            renewed = output.count("Successfully renewed")

            logger.info(f"✅ Renovação concluída: {renewed} certificados renovados")
            return renewed, 0

        except Exception as e:
            logger.error(f"❌ Erro ao renovar certificados: {str(e)}")
            return 0, 1

    def delete_certificate(self, domain: str) -> tuple[bool, str]:
        """
        Remove certificado de um domínio

        Args:
            domain: Domínio para remover certificado

        Returns:
            (sucesso, mensagem)
        """
        try:
            if not self.domain_has_certificate(domain):
                return True, f"Domínio {domain} não tem certificado"

            cmd = [self.certbot_path, "delete", "--cert-name", domain, "--non-interactive"]

            logger.info(f"Removendo certificado de {domain}...")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                logger.info(f"✅ Certificado removido: {domain}")
                return True, "Certificado removido com sucesso"
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"❌ Erro ao remover certificado de {domain}: {error_msg}")
                return False, f"Erro ao remover: {error_msg}"

        except Exception as e:
            logger.error(f"❌ Exceção ao remover certificado de {domain}: {str(e)}")
            return False, f"Erro inesperado: {str(e)}"

    def get_certificate_info(self, domain: str) -> dict:
        """
        Obtém informações sobre o certificado de um domínio

        Args:
            domain: Domínio para obter informações

        Returns:
            Dicionário com informações do certificado
        """
        try:
            cmd = [self.certbot_path, "certificates", "-d", domain]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                output = result.stdout

                # Extrair informações básicas
                info = {"domain": domain, "has_certificate": self.domain_has_certificate(domain), "raw_output": output}

                # Extrair data de expiração (se existir)
                if "Expiry Date:" in output:
                    expiry_line = [line for line in output.split("\n") if "Expiry Date:" in line][0]
                    info["expiry_date"] = expiry_line.split("Expiry Date:")[1].strip()

                return info
            else:
                return {"domain": domain, "has_certificate": False, "error": "Certificado não encontrado"}

        except Exception as e:
            logger.error(f"❌ Erro ao obter info do certificado de {domain}: {str(e)}")
            return {"domain": domain, "has_certificate": False, "error": str(e)}


# Instância global
ssl_manager = SSLManager()













