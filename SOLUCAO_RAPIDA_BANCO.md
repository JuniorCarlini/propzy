# ⚡ Solução Rápida: Erro "database propzy_user does not exist"

## 🎯 Problema

Algum serviço está tentando conectar ao banco `propzy_user` que não existe. O banco correto é `propzy`.

## ✅ SOLUÇÃO RÁPIDA

### Opção 1: Criar o Banco (Mais Rápido)

```bash
# Criar o banco propzy_user
docker exec -it propzy-db psql -U propzy -d postgres -c "CREATE DATABASE propzy_user;"

# Verificar se foi criado
docker exec -it propzy-db psql -U propzy -d postgres -c "\l" | grep propzy
```

### Opção 2: Corrigir Variável de Ambiente (Recomendado)

O problema está na variável `DB_NAME` que está como `propzy_user` em algum lugar.

#### No Portainer:

1. **Stacks** → Sua stack → **Editor**
2. Procure `DB_NAME` nas variáveis de ambiente
3. Altere para `propzy` (não `propzy_user`)
4. **Update the stack**

#### Verificar onde está errado:

```bash
# Ver variáveis de ambiente de todos os serviços
docker exec propzy-app env | grep DB_NAME
docker exec propzy-celery-worker env | grep DB_NAME
docker exec propzy-celery-beat env | grep DB_NAME
```

## 🔍 DIAGNÓSTICO

O erro mostra que está tentando conectar repetidamente, o que significa:

- ✅ Django app está usando `propzy` (correto)
- ❌ Algum outro serviço (Celery?) está usando `propzy_user` (errado)

## 📋 CHECKLIST

- [ ] Verificar variável `DB_NAME` em **todos os serviços** (app, celery-worker, celery-beat)
- [ ] Deve ser `propzy` em todos
- [ ] Reiniciar serviços após alterar
- [ ] Verificar logs: `docker logs propzy-app --tail 50`

## 🚀 COMANDO COMPLETO

```bash
# 1. Criar banco (solução rápida)
docker exec -it propzy-db psql -U propzy -d postgres -c "CREATE DATABASE propzy_user;"

# 2. OU corrigir variável no Portainer e reiniciar
# (Melhor solução a longo prazo)
```



