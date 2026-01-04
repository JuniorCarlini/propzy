# 🔐 SSL Automático para Domínios Personalizados

## ✨ O QUE É?

Sistema **100% automático e grátis** que gera certificados SSL (Let's Encrypt) para domínios personalizados dos clientes.

**Como funciona:**
1. Cliente adiciona domínio personalizado no Admin (`www.seudominio.com.br`)
2. Cliente aponta **CNAME** do domínio para `propzy.com.br`
3. Sistema **detecta automaticamente** e gera certificado SSL
4. Certificado **renova sozinho** a cada 60 dias
5. **Zero trabalho manual!** 🎉

---

## 🚀 CONFIGURAÇÃO INICIAL (Uma Vez)

### 1. Executar Script de Setup

```bash
cd /opt/propzy
./scripts/setup_ssl_auto.sh
```

Este script:
- ✅ Cria diretório webroot para Let's Encrypt
- ✅ Verifica/instala Certbot
- ✅ Configura NGINX para ACME challenge
- ✅ Configura renovação automática (cron)

### 2. Reiniciar NGINX

```bash
docker restart propzy-nginx
```

### 3. Fazer Migrations (adiciona campos no banco)

```bash
docker exec propzy-app python manage.py makemigrations
docker exec propzy-app python manage.py migrate
```

### 4. Configurar Celery Beat (renovação automática)

Edite `/opt/propzy/config/celery.py` e adicione:

```python
from celery.schedules import crontab

# Configuração do Celery Beat
app.conf.beat_schedule = {
    'renew-ssl-certificates-daily': {
        'task': 'apps.landings.tasks.renew_ssl_certificates',
        'schedule': crontab(hour=3, minute=0),  # Todo dia às 3h
    },
}
```

Reiniciar Celery Beat:

```bash
docker restart propzy-celery-beat
```

---

## 📋 COMO USAR (Para Clientes)

### Para o Cliente:

1. **Acessar Admin:** `https://propzy.com.br/admin/`
2. **Landings → Landing Pages** → Editar sua landing page
3. **Campo "Domínio Personalizado":** Preencher com `www.seudominio.com.br`
4. **Salvar**

### Configurar DNS (Cliente faz):

No painel de DNS do domínio (ex: Registro.br, GoDaddy, etc):

```
Tipo:    CNAME
Nome:    www
Destino: propzy.com.br
TTL:     Automático
```

**OU se quiser sem "www":**

```
Tipo:    A
Nome:    @
IP:      72.60.252.168 (IP do seu servidor)
```

---

## 🤖 FUNCIONAMENTO AUTOMÁTICO

### O que acontece automaticamente:

```
1. Cliente adiciona domínio no Admin
   ↓
2. Signal detecta mudança (apps/landings/signals.py)
   ↓
3. Aguarda 30s → Verifica DNS (task: check_custom_domain_dns)
   ↓
4. Aguarda 2min → Gera certificado SSL (task: generate_ssl_certificate)
   ↓
5. Certificado gerado! ✅
   ↓
6. A cada 60 dias → Renova automaticamente
```

### Campos no Admin:

Ao editar Landing Page, verá:

- **Status SSL:** none / generating / active / error
- **Status DNS:** pending / ok / error
- **Erro SSL:** (se houver erro na geração)
- **Erro DNS:** (se DNS não estiver configurado)

---

## 🔧 COMANDOS MANUAIS

### Gerar Certificado Manualmente

```bash
docker exec propzy-app python manage.py manage_ssl generate \
  --domain www.dominio-cliente.com.br \
  --email contato@dominio-cliente.com.br
```

### Listar Todos os Certificados

```bash
docker exec propzy-app python manage.py manage_ssl list
```

**Saída:**
```
📋 Landing Pages com Domínios Personalizados:

🔒 ✅ www.imobiliaria1.com.br (Imobiliária 1) - Status: Ativo
🔓 ⏳ www.imobiliaria2.com.br (Imobiliária 2) - Status: Gerando...
🔒 ❌ www.imobiliaria3.com.br (Imobiliária 3) - Status: Erro
   └─ Erro: DNS não configurado...
```

### Renovar Certificado Específico

```bash
docker exec propzy-app python manage.py manage_ssl renew \
  --domain www.dominio-cliente.com.br
```

### Renovar Todos os Certificados

```bash
docker exec propzy-app python manage.py manage_ssl renew-all
```

### Verificar Status de Certificado

```bash
docker exec propzy-app python manage.py manage_ssl check \
  --domain www.dominio-cliente.com.br
```

### Remover Certificado

```bash
docker exec propzy-app python manage.py manage_ssl delete \
  --domain www.dominio-cliente.com.br
```

---

## 🔄 RENOVAÇÃO AUTOMÁTICA

### Método 1: Celery Beat (Recomendado)

**Vantagem:** Integrado com Django, logs no Admin

```python
# Em config/celery.py
app.conf.beat_schedule = {
    'renew-ssl-certificates-daily': {
        'task': 'apps.landings.tasks.renew_ssl_certificates',
        'schedule': crontab(hour=3, minute=0),
    },
}
```

### Método 2: Cron (Alternativa)

**Vantagem:** Funciona mesmo se Celery cair

```bash
# Adicionar ao crontab
crontab -e

# Adicionar linha:
0 3 * * * docker exec propzy-app python manage.py manage_ssl renew-all >> /var/log/ssl-renew.log 2>&1
```

**Ambos os métodos podem rodar simultaneamente!**

---

## 🛠️ TROUBLESHOOTING

### 1. Certificado não é gerado

**Verificar:**

```bash
# 1. Verificar logs do container
docker logs propzy-app --tail 100

# 2. Verificar DNS
nslookup www.dominio-cliente.com.br

# 3. Verificar se aponta para seu servidor
dig www.dominio-cliente.com.br

# 4. Tentar manualmente
docker exec propzy-app python manage.py manage_ssl generate \
  --domain www.dominio-cliente.com.br \
  --email email@exemplo.com
```

**Causas comuns:**
- ❌ DNS não configurado ou não propagado ainda (aguardar 5-10 min)
- ❌ Domínio aponta para IP errado
- ❌ Firewall bloqueando porta 80 (Let's Encrypt precisa!)
- ❌ NGINX não configurado corretamente para `/.well-known/acme-challenge/`

### 2. Erro "Rate limit exceeded"

Let's Encrypt tem limites:
- **5 certificados** por domínio por semana
- **50 certificados** por conta por semana

**Solução:** Aguardar 1 semana ou usar domínios diferentes

### 3. Erro "Connection refused"

```bash
# Verificar se porta 80 está aberta
netstat -tlnp | grep :80

# Verificar firewall
ufw status

# Se bloqueado, liberar porta 80
ufw allow 80/tcp
```

### 4. Certificado não renova

```bash
# Testar renovação manual
docker exec propzy-app python manage.py manage_ssl renew-all

# Verificar cron
crontab -l

# Verificar Celery Beat
docker logs propzy-celery-beat --tail 50
```

### 5. NGINX não encontra certificado

**Verificar se certificado existe:**

```bash
ls -la /etc/letsencrypt/live/www.dominio-cliente.com.br/
```

**Se não existir:**

```bash
docker exec propzy-app python manage.py manage_ssl generate \
  --domain www.dominio-cliente.com.br
```

---

## 📊 MONITORAMENTO

### Ver Status no Admin

1. **Admin → Landings → Landing Pages**
2. Campos **Status SSL** e **Status DNS** mostram status atual
3. Campo **Erro SSL** mostra mensagem de erro (se houver)

### Logs

```bash
# Logs do app (geração de certificados)
docker logs propzy-app -f | grep SSL

# Logs do Celery Worker
docker logs propzy-celery-worker -f

# Logs do Celery Beat
docker logs propzy-celery-beat -f

# Logs de renovação (cron)
tail -f /var/log/ssl-renew.log
```

### Listar Certificados Ativos

```bash
# Via comando
docker exec propzy-app python manage.py manage_ssl list

# Via Certbot
docker exec propzy-app certbot certificates
```

---

## 💰 CUSTOS

**✅ TOTALMENTE GRÁTIS!**

- Let's Encrypt: Grátis
- Renovação automática: Grátis
- Certificados ilimitados: Grátis

**Limites:**
- 5 certificados por domínio por semana
- 50 certificados por conta por semana
- 300 pedidos por domínio por 3 horas

**(Suficiente para 99% dos casos!)**

---

## 🎯 RESUMO

### Para Administrador (você):

1. ✅ Executar `./scripts/setup_ssl_auto.sh` (uma vez)
2. ✅ Configurar Celery Beat (uma vez)
3. ✅ Pronto! Sistema roda sozinho

### Para Cliente:

1. ✅ Adicionar domínio no Admin
2. ✅ Configurar CNAME no DNS
3. ✅ Aguardar 2-5 minutos
4. ✅ SSL funcionando! 🎉

### O que o sistema faz sozinho:

- ✅ Detecta novo domínio
- ✅ Verifica DNS
- ✅ Gera certificado SSL
- ✅ Configura NGINX
- ✅ Renova a cada 60 dias
- ✅ Notifica administradores (email)
- ✅ Atualiza status no Admin

---

## 🔒 SEGURANÇA

- ✅ Certificados Let's Encrypt (confiados por todos os navegadores)
- ✅ SSL/TLS 1.2+ (moderno e seguro)
- ✅ Renovação automática (nunca expira)
- ✅ Chaves privadas seguras (armazenadas em `/etc/letsencrypt/`)
- ✅ Logs auditáveis

---

## 📚 ARQUIVOS IMPORTANTES

```
apps/landings/
├── ssl_manager.py        # Gerenciador de SSL
├── tasks.py              # Tarefas Celery (geração/renovação)
├── signals.py            # Detecta domínios novos
├── models.py             # Campos: ssl_status, dns_status
└── management/commands/
    └── manage_ssl.py     # Comandos manuais

scripts/
└── setup_ssl_auto.sh     # Script de configuração inicial

/etc/letsencrypt/         # Certificados SSL
/var/www/certbot/         # Webroot para ACME challenge
```

---

## ✅ CHECKLIST DE CONFIGURAÇÃO

- [ ] Executar `./scripts/setup_ssl_auto.sh`
- [ ] Reiniciar NGINX
- [ ] Fazer migrations
- [ ] Configurar Celery Beat
- [ ] Testar com domínio de teste
- [ ] Verificar renovação automática (cron ou Celery)
- [ ] Verificar logs
- [ ] Documentar para clientes (como configurar DNS)

---

## 🎉 PRONTO!

**Sistema funcionando 100% automático!**

- ✅ Certificados SSL grátis
- ✅ Geração automática
- ✅ Renovação automática
- ✅ Zero trabalho manual
- ✅ Escalável para milhares de domínios

**BOA SORTE! 🚀**

