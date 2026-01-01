# 🚀 Como Rodar o Sistema Localmente

Guia rápido para rodar o Propzy no seu ambiente de desenvolvimento.

## 📋 Pré-requisitos

- **Docker Desktop** instalado e rodando
- **Git** instalado

## ⚡ Método Rápido (Recomendado)

Execute o script automatizado:

```bash
# Dar permissão de execução (primeira vez)
chmod +x scripts/dev/dev-start.sh

# Rodar o sistema
./scripts/dev/dev-start.sh
```

Pronto! O sistema estará disponível em **http://localhost:8001**

### 🔐 Credenciais de Acesso

- **Email:** `admin@propzy.local`
- **Senha:** `admin123`

---

## 🔧 Método Manual

Se preferir rodar manualmente:

### 1. Entrar no diretório do docker-compose de desenvolvimento

```bash
cd infra/dev
```

### 2. Subir os serviços

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

### 3. Executar migrações

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### 4. Criar superusuário (se necessário)

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@propzy.local').exists():
    User.objects.create_superuser(
        email='admin@propzy.local',
        password='admin123',
        first_name='Admin',
        last_name='Propzy'
    )
    print('✅ Superusuário criado')
else:
    print('✅ Superusuário já existe')
PYTHON
```

### 5. Criar grupos padrão

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py create_groups
```

---

## 🌐 URLs de Acesso

Após iniciar o sistema, você terá acesso a:

- **🌐 Aplicação:** http://localhost:8001
- **🔐 Admin Django:** http://localhost:8001/admin/
- **📧 MailHog (emails):** http://localhost:8026
- **🗄️ PostgreSQL:** localhost:5433
- **📦 Redis:** localhost:6380

---

## 📋 Comandos Úteis

### Ver logs

```bash
cd infra/dev
docker compose -f docker-compose.dev.yml logs -f
```

### Ver logs apenas do Django

```bash
cd infra/dev
docker compose -f docker-compose.dev.yml logs -f web
```

### Parar o sistema

```bash
cd infra/dev
docker compose -f docker-compose.dev.yml down
```

### Reiniciar serviços

```bash
cd infra/dev
docker compose -f docker-compose.dev.yml restart
```

### Acessar shell do Django

```bash
cd infra/dev
docker compose -f docker-compose.dev.yml exec web python manage.py shell
```

### Criar migração

```bash
cd infra/dev
docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations
```

### Aplicar migrações

```bash
cd infra/dev
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### Coletar arquivos estáticos

```bash
cd infra/dev
docker compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput
```

---

## 🐛 Troubleshooting

### Docker não está rodando

```bash
# Verificar se Docker está rodando
docker info

# Se não estiver, inicie o Docker Desktop
```

### Porta já está em uso

Se a porta 8001 estiver ocupada, você pode:

1. Parar o processo que está usando a porta
2. Ou modificar a porta no arquivo `infra/dev/docker-compose.dev.yml`:

```yaml
ports:
  - "8002:8000"  # Mude 8001 para outra porta
```

### Containers não sobem

```bash
# Ver logs detalhados
cd infra/dev
docker compose -f docker-compose.dev.yml logs

# Reconstruir do zero
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d --build
```

### Erro de migração

```bash
# Resetar banco (CUIDADO: apaga todos os dados!)
cd infra/dev
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
```

---

## 📝 Notas Importantes

- **Hot Reload:** O código Python é montado como volume, então mudanças no código são refletidas automaticamente (após alguns segundos)
- **Banco de Dados:** Os dados ficam persistidos em volumes Docker, então não são perdidos ao parar os containers
- **Emails:** Em desenvolvimento, todos os emails são capturados pelo MailHog e podem ser visualizados em http://localhost:8026
- **Debug:** O modo DEBUG está ativado por padrão em desenvolvimento

---

**✨ Bom desenvolvimento!**


