# 🚨 CORREÇÃO URGENTE - EasyPanel

## ✅ Correções Feitas

1. **Redis**: Removida a senha (estava causando erro `requirepass wrong number of arguments`)
2. **Variáveis**: Formato correto para EasyPanel ler

---

## 📤 PASSO 1: Fazer Push

No seu terminal (Mac ou Cursor):

```bash
cd /Users/juniorcarlini/Documents/GitHub/propzy
git push origin main
```

---

## 🔐 PASSO 2: Configurar Variáveis no EasyPanel

### **IMPORTANTE**: As variáveis precisam estar SALVAS E APLICADAS!

1. **No EasyPanel**, vá em: **Projeto → Services → propzy → Environment Variables**

2. **Verifique se TODAS estas variáveis estão lá:**

```bash
# =========================================
# OBRIGATÓRIAS (SEM ESSAS NÃO FUNCIONA!)
# =========================================
SECRET_KEY=SEU_SECRET_KEY_AQUI_50_CARACTERES_MINIMO
DB_PASSWORD=SUA_SENHA_POSTGRES_SEGURA
ALLOWED_HOSTS=propzy.com.br,app.propzy.com.br,*.propzy.com.br

# =========================================
# OPCIONAIS (mas recomendadas)
# =========================================
VPS_IP=167.88.54.162
PROXY_DOMAIN=proxy.propzy.com.br
```

3. **Gerar SECRET_KEY** (se não tiver):
   - No terminal do Mac:
   ```bash
   openssl rand -base64 50
   ```
   - Copie o resultado e cole no EasyPanel

4. **Criar senha do banco** (se não tiver):
   - No terminal do Mac:
   ```bash
   openssl rand -base64 32
   ```
   - Copie o resultado e cole no EasyPanel

5. **CLIQUE EM "SAVE" ou "SALVAR"** ← **CRÍTICO!**

---

## 🔄 PASSO 3: Atualizar o Código e Redeployar

### Opção A: Pull do GitHub (Recomendado)

No EasyPanel:
1. Vá em **Services → propzy**
2. Procure botão **"Pull"** ou **"Update"** ou ícone ↻
3. Clique e aguarde o pull
4. Clique em **"Deploy"** ou **"Redeploy"**

### Opção B: Recriar o Serviço (Se não achar o botão Pull)

1. **Pare o serviço** (botão Stop)
2. **Delete o serviço** (mas NÃO delete volumes!)
3. **Recrie** usando o GitHub (mesma URL)
4. **Configure as variáveis de novo** (copie e cole as de cima)
5. **Deploy**

---

## 🧪 PASSO 4: Verificar se Funcionou

Depois do deploy, verifique os logs:

### ✅ Logs CORRETOS (significa que funcionou):

```
web-1  | ✅ Entrypoint concluído!
web-1  | Starting gunicorn...
redis-1 | Ready to accept connections
celery-1 | [2025-01-02 ...] celery@... ready
```

### ❌ Logs ERRADOS (ainda tem problema):

```
ValueError: SECRET_KEY environment variable is required
redis: requirepass wrong number of arguments
```

---

## 💡 DICAS DE TROUBLESHOOTING

### Se ainda der erro de SECRET_KEY:

1. **No EasyPanel**, vá em **Environment Variables**
2. Verifique se o `SECRET_KEY` está lá
3. **Delete a variável** e **crie de novo** (as vezes o EasyPanel não salva direito)
4. Certifique-se de clicar em **"Save"**
5. **Redeploy** o serviço

### Se Redis ainda der erro:

O docker-compose já foi corrigido. Só precisa:
1. Fazer o **pull** do código atualizado (Passo 3)
2. **Redeployar**

---

## 📞 PRÓXIMO PASSO

Depois de fazer tudo isso, me envie:
- ✅ Os logs atualizados (últimas 50 linhas)
- ✅ Print da tela de Environment Variables (pode tapar valores sensíveis)

Vamos resolver! 🚀

