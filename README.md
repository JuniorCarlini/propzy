# Propzy - SaaS Multi-Tenant

Sistema SaaS escalável para imobiliárias com suporte a domínios personalizados, deploy automático e segurança máxima.

## 🚀 Quick Start

### Deploy Automático (Recomendado)

1. **Configure GitHub Secrets:**
   - `VPS_SSH_PRIVATE_KEY`
   - `VPS_IP`

2. **Faça push:**
   ```bash
   git push origin main
   ```

3. **Pronto!** Deploy automático via GitHub Actions.

### Deploy Manual

Veja [DEPLOY.md](DEPLOY.md) para instruções completas.

---

## 🏗️ Arquitetura

- **Multi-tenant** baseado em domínio
- **Django 5.x** + PostgreSQL + Redis
- **Docker** + Docker Compose
- **Nginx** como reverse proxy
- **Let's Encrypt** para SSL automático
- **Cloudflare** para DNS e CDN

Consulte [ARCHITECTURE.md](ARCHITECTURE.md) para detalhes.

---

## 🔒 Segurança

- ✅ Firewall configurado (UFW)
- ✅ Fail2Ban ativado
- ✅ SSL/TLS automático (Let's Encrypt)
- ✅ Rate limiting
- ✅ CSRF protection dinâmico
- ✅ Headers de segurança

---

## 📁 Estrutura

```
propzy/
├── backend/          # Aplicação Django
├── infra/            # Docker, Nginx, Scripts
└── .github/          # GitHub Actions
```

---

## 📚 Documentação

Consulte a [documentação completa](./docs/README.md) para:
- 🏗️ [Arquitetura](./docs/architecture/ARCHITECTURE.md) - Arquitetura completa do sistema
- 🚀 [Deploy](./docs/deployment/DEPLOY.md) - Guia de deploy inicial
- 🔐 [Segurança](./docs/security/MELHORIAS-IMPLEMENTADAS.md) - Melhorias de segurança
- 📋 [Guias](./docs/guides/SETUP-RESUMO.md) - Guias rápidos

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abra Pull Request

---

**Desenvolvido com segurança e escalabilidade em mente** 🔐




