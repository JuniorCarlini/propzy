# 🔧 Corrigir Erro 500 Após Reset do Banco

## 🎯 Problema
Após apagar o banco e subir novamente, está dando erro 500.

## 🔍 DIAGNÓSTICO RÁPIDO

### 1. Verificar Logs do Django

```bash
# No contêiner da aplicação
docker exec -it propzy-app bash
tail -f /var/log/gunicorn/error.log

# OU ver logs do Docker
docker logs propzy-app --tail 100
```

### 2. Verificar Migrações

```bash
# Dentro do contêiner
python manage.py showmigrations

# Verificar se todas estão aplicadas
python manage.py migrate --run-syncdb
```

### 3. Verificar Banco de Dados

```bash
# Acessar banco
docker exec -it propzy-db psql -U propzy -d propzy

# Verificar tabelas
\dt

# Verificar migrações aplicadas
SELECT * FROM django_migrations ORDER BY app, name;

# Verificar se há sites
SELECT COUNT(*) FROM landings_site;

# Sair
\q
```

---

## ✅ SOLUÇÕES

### Solução 1: Aplicar Migrações Novamente

```bash
# Entrar no contêiner
docker exec -it propzy-app bash

# Aplicar todas as migrações
python manage.py migrate

# Criar superusuário (se necessário)
python manage.py createsuperuser
```

### Solução 2: Verificar se há Dados Necessários

O erro pode ser porque:

1. **Não há Site criado** - O middleware está tentando encontrar um site
2. **Não há Theme** - O site precisa de um tema
3. **Não há User** - Precisa de pelo menos um usuário

**Criar dados básicos:**

```bash
# Dentro do shell do Django
python manage.py shell

# Criar superusuário
from apps.core.models import User
user = User.objects.create_superuser(
    email='admin@propzy.com.br',
    password='admin123'
)

# Criar site para o usuário
from apps.landings.models import Site
from apps.themes.models import Theme

# Pegar primeiro tema disponível
theme = Theme.objects.first()
if not theme:
    print("ERRO: Não há temas instalados!")
    print("Execute: python manage.py install_themes")
else:
    site = Site.objects.create(
        owner=user,
        subdomain='admin',
        business_name='Propzy',
        theme=theme
    )
    print(f"Site criado: {site.subdomain}")
```

### Solução 3: Verificar Configuração do Middleware

O erro pode ser no `TenantMiddleware`. Verifique:

```python
# config/settings.py
MIDDLEWARE = [
    # ...
    'apps.landings.middleware.TenantMiddleware',  # Deve estar aqui
    # ...
]
```

### Solução 4: Verificar ALLOWED_HOSTS

```bash
# Verificar variável de ambiente
docker exec -it propzy-app env | grep ALLOWED_HOSTS

# Deve estar configurado corretamente
# Ex: ALLOWED_HOSTS=propzy.com.br,www.propzy.com.br,localhost
```

### Solução 5: Verificar Logs de Erro Específicos

```bash
# Ver último erro completo
docker exec -it propzy-app python manage.py check --deploy

# Ver traceback completo (se DEBUG=True)
# Acesse a URL e veja o traceback na página de erro
```

---

## 🚨 ERROS COMUNS

### Erro: "Site não encontrado"
**Causa**: Middleware não encontrou site para o domínio

**Solução**:
- Criar um site no admin
- Ou acessar via domínio do sistema (localhost, propzy.com.br)

### Erro: "Theme.DoesNotExist"
**Causa**: Não há temas instalados

**Solução**:
```bash
python manage.py install_themes
```

### Erro: "RelatedObjectDoesNotExist: User has no site"
**Causa**: Usuário não tem site associado

**Solução**: Criar site para o usuário (veja Solução 2)

### Erro: "Table 'django_migrations' doesn't exist"
**Causa**: Migrações não foram aplicadas

**Solução**:
```bash
python manage.py migrate
```

---

## 📋 CHECKLIST DE VERIFICAÇÃO

Execute estes comandos em ordem:

```bash
# 1. Verificar migrações
python manage.py showmigrations | grep "\[ \]"

# 2. Aplicar migrações pendentes
python manage.py migrate

# 3. Verificar se há temas
python manage.py shell -c "from apps.themes.models import Theme; print('Temas:', Theme.objects.count())"

# 4. Verificar se há usuários
python manage.py shell -c "from apps.core.models import User; print('Usuários:', User.objects.count())"

# 5. Verificar se há sites
python manage.py shell -c "from apps.landings.models import Site; print('Sites:', Site.objects.count())"

# 6. Verificar configuração
python manage.py check
```

---

## 🎯 SOLUÇÃO RÁPIDA (Tudo de Uma Vez)

```bash
# Entrar no contêiner
docker exec -it propzy-app bash

# 1. Aplicar migrações
python manage.py migrate

# 2. Instalar temas (se necessário)
python manage.py install_themes

# 3. Criar superusuário (se não existir)
python manage.py createsuperuser

# 4. Verificar tudo
python manage.py check
python manage.py showmigrations
```

---

## 📞 Se Nada Funcionar

1. **Ver traceback completo**: Acesse a URL com DEBUG=True e veja o erro
2. **Ver logs do Gunicorn**: `tail -f /var/log/gunicorn/error.log`
3. **Ver logs do Docker**: `docker logs propzy-app --tail 200`
4. **Verificar banco**: Conecte no PostgreSQL e verifique as tabelas

---

## ✅ Após Corrigir

Teste acessando:
- `http://propzy.com.br/` - Página inicial
- `http://propzy.com.br/admin/` - Admin do Django
- `http://propzy.com.br/accounts/login/` - Login



