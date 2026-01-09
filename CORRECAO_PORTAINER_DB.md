# 🔧 Correção: Erro "database propzy_user does not exist" no Portainer

## 🎯 Problema Identificado

Nas variáveis de ambiente do Portainer você tem:
- `DB_NAME=propzy_prod` ✅ (nome do banco)
- `DB_USER=propzy_user` ✅ (usuário do banco)

Mas o PostgreSQL está tentando conectar ao banco `propzy_user` (que é o usuário, não o banco!).

## ✅ SOLUÇÃO

### Passo 1: Verificar se o banco `propzy_prod` existe

No Portainer, abra o **Console** do contêiner `propzy-db` e execute:

```sql
\l
```

Deve mostrar o banco `propzy_prod`. Se não existir, crie:

```sql
CREATE DATABASE propzy_prod;
```

### Passo 2: Verificar Variáveis de Ambiente em TODOS os Serviços

No Portainer, verifique as variáveis `DB_NAME` em **TODOS** os serviços:

1. **app** (propzy-app)
2. **celery-worker** (propzy-celery-worker)
3. **celery-beat** (propzy-celery-beat)

**Todos devem ter:**
- `DB_NAME=propzy_prod` ✅
- `DB_USER=propzy_user` ✅
- `DB_PASSWORD=Propzy2026DB@Secure!#$` ✅
- `DB_HOST=db` ✅
- `DB_PORT=5432` ✅

### Passo 3: Verificar docker-compose.prod.yml

O arquivo deve estar assim:

```yaml
app:
  environment:
    - DB_NAME=${DB_NAME}  # Deve pegar propzy_prod
    - DB_USER=${DB_USER}  # Deve pegar propzy_user
    # ... outras variáveis

celery-worker:
  environment:
    - DB_NAME=${DB_NAME}  # IMPORTANTE: Deve ter isso também!
    - DB_USER=${DB_USER}
    # ... outras variáveis

celery-beat:
  environment:
    - DB_NAME=${DB_NAME}  # IMPORTANTE: Deve ter isso também!
    - DB_USER=${DB_USER}
    # ... outras variáveis
```

## 🔍 DIAGNÓSTICO

O erro acontece porque:

1. ✅ Variável `DB_NAME` está definida como `propzy_prod` no Portainer
2. ❌ Mas algum serviço (provavelmente Celery) não está recebendo essa variável
3. ❌ Então está usando `DB_USER` (propzy_user) como nome de banco por padrão

## 📋 CHECKLIST NO PORTAINER

- [ ] Verificar se `DB_NAME=propzy_prod` está em **TODOS** os serviços
- [ ] Verificar se o banco `propzy_prod` existe no PostgreSQL
- [ ] Reiniciar todos os serviços após corrigir
- [ ] Verificar logs: `docker logs propzy-db --tail 50`

## 🚀 SOLUÇÃO RÁPIDA

### Opção 1: Criar o banco propzy_user (temporário)

```sql
-- No console do propzy-db
CREATE DATABASE propzy_user;
```

### Opção 2: Corrigir variáveis (correto)

1. No Portainer: **Stacks** → Sua stack → **Editor**
2. Verifique se `DB_NAME` está em **TODOS** os serviços
3. Se faltar em algum serviço (especialmente celery-worker e celery-beat), adicione:
   ```
   DB_NAME=propzy_prod
   ```
4. **Update the stack**

## ⚠️ IMPORTANTE

O problema está na configuração do Portainer, não no código. Verifique se:

- ✅ Todos os serviços têm acesso à variável `DB_NAME`
- ✅ O banco `propzy_prod` existe no PostgreSQL
- ✅ As variáveis estão sendo passadas corretamente no docker-compose



