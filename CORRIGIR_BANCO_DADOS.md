# 🔧 Corrigir Erro: database "propzy_user" does not exist

## 🎯 Problema

O PostgreSQL está tentando conectar ao banco `propzy_user` que não existe. O banco correto é `propzy`.

**Erro**: `FATAL: database "propzy_user" does not exist`

## ✅ SOLUÇÃO

### Opção 1: Criar o Banco "propzy_user" (Rápido)

```bash
# Entrar no contêiner do PostgreSQL
docker exec -it propzy-db psql -U propzy -d postgres

# Criar o banco de dados
CREATE DATABASE propzy_user;

# Sair
\q
```

### Opção 2: Corrigir Variável de Ambiente (Recomendado)

A variável `DB_NAME` está configurada como `propzy_user` quando deveria ser `propzy`.

#### No Portainer:

1. Vá em **Stacks** → Sua stack
2. Clique em **Editor**
3. Procure por `DB_NAME` nas variáveis de ambiente
4. Altere de `propzy_user` para `propzy`
5. Clique em **Update the stack**

#### Ou via arquivo .env:

```bash
# Editar variável de ambiente
DB_NAME=propzy  # Não propzy_user!
```

### Opção 3: Verificar e Corrigir no Docker Compose

Verifique o arquivo `docker-compose.prod.yml`:

```yaml
environment:
  - POSTGRES_DB=${DB_NAME}  # Deve ser "propzy"
```

E certifique-se de que a variável `DB_NAME` está definida como `propzy`.

---

## 🔍 VERIFICAÇÃO

Após corrigir, verifique:

```bash
# Verificar bancos existentes
docker exec -it propzy-db psql -U propzy -d postgres -c "\l"

# Deve mostrar:
# propzy        | propzy | UTF8     | en_US.utf8 | en_US.utf8 |
```

---

## 📋 CHECKLIST

- [ ] Verificar variável `DB_NAME` no Portainer/arquivo .env
- [ ] Deve ser `propzy` (não `propzy_user`)
- [ ] Reiniciar contêineres após alterar variável
- [ ] Verificar se banco existe: `docker exec -it propzy-db psql -U propzy -d propzy -c "\dt"`

---

## 🚀 COMANDO RÁPIDO

Se quiser criar o banco rapidamente:

```bash
docker exec -it propzy-db psql -U propzy -d postgres -c "CREATE DATABASE propzy_user;"
```

Mas o **recomendado** é corrigir a variável de ambiente para usar `propzy` que já existe.



