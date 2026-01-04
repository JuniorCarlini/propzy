# ⚡ Início Rápido com Portainer

## 🎯 Seu Checklist Simplificado

### Antes de Começar:
- [x] VPS com Portainer instalado
- [ ] Domínio registrado
- [ ] Conta Cloudflare (grátis)

---

## 🚀 5 Passos para Colocar no Ar

### 1. DNS (5 min)
**Cloudflare → DNS:**
```
Tipo: A    | Nome: @  | IP: seu_servidor
Tipo: A    | Nome: *  | IP: seu_servidor  ← WILDCARD
Tipo: CNAME| Nome: www| Destino: propzy.com.br
```

### 2. SSL (10 min)
**Via SSH:**
```bash
apt install certbot -y
certbot certonly --manual --preferred-challenges dns \
  -d propzy.com.br -d *.propzy.com.br
```
Siga instruções → Adicione TXT no Cloudflare → Enter

### 3. Upload Código (5 min)
**Via SSH ou SFTP:**
```bash
mkdir -p /opt/propzy
cd /opt/propzy
git clone https://github.com/seu-usuario/propzy.git .
# OU faça upload via SFTP para /opt/propzy/
```

### 4. Configurar .env (5 min)
**Via SSH:**
```bash
cd /opt/propzy
cp .env.prod.example .env.prod
nano .env.prod
```

**Edite (mínimo necessário):**
```bash
SECRET_KEY=cole-chave-gerada-aqui
DEBUG=False
BASE_DOMAIN=propzy.com.br
ALLOWED_HOSTS=.propzy.com.br,propzy.com.br
DB_PASSWORD=senha-forte-123
REDIS_PASSWORD=senha-forte-456
```

### 5. Deploy no Portainer (10 min)

#### 5.1 Acessar Portainer
```
http://seu-servidor:9000
```

#### 5.2 Criar Stack
1. **Stacks** → **Add stack**
2. Nome: `propzy`
3. Build method: **Web editor**
4. Copie o conteúdo de `PORTAINER_STACK.txt`
5. Cole no editor
6. **Deploy the stack**
7. Aguarde 2-3 minutos

#### 5.3 Inicializar
**Portainer → Containers → propzy-app → Console:**

Ou via SSH:
```bash
docker exec propzy-app python manage.py migrate
docker exec propzy-app python manage.py collectstatic --noinput
docker exec propzy-app python manage.py install_themes
docker exec -it propzy-app python manage.py createsuperuser
```

---

## ✅ Pronto! Testar:

1. **Admin:** `https://propzy.com.br/admin/`
2. **Criar Landing Page** no admin
3. **Acessar:** `https://teste.propzy.com.br`

**Funcionou! 🎉**

---

## 🎛️ Usar o Portainer

### Ver Logs:
1. Containers → Clique em `propzy-app`
2. **Logs** → Auto-refresh

### Reiniciar:
1. Containers → Selecione container
2. **Restart**

### Executar Comando:
1. Containers → Clique em `propzy-app`
2. **Console** → Command: `/bin/sh`
3. **Connect**

### Atualizar Sistema:
1. SSH: `cd /opt/propzy && git pull`
2. Portainer → Stacks → `propzy` → **Editor**
3. **Update the stack** → ✅ Re-pull and redeploy

---

## 🆘 Problemas?

**Container não inicia:**
- Portainer → Containers → propzy-app → **Logs**
- Veja o erro (geralmente .env.prod)

**Landing page 404:**
- Verifique se está **Publicada** no Admin
- Ver logs do container

**SSL não funciona:**
```bash
certbot renew --force-renewal
docker restart propzy-nginx
```

---

## 📚 Documentação Completa

**Leia:** `DEPLOY.md` (passo a passo detalhado)

---

**Tempo Total:** 30-45 minutos
**Dificuldade:** ⭐⭐ (Fácil)
**Interface:** 100% Visual (Portainer)

**Boa sorte! 🚀**

