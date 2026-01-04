# ⚡ INÍCIO RÁPIDO - Desenvolvimento Local

Guia de 5 minutos para rodar o sistema localmente.

---

## 📋 PRÉ-REQUISITOS

- Python 3.13+
- PostgreSQL 17
- Redis 7
- UV (gerenciador de pacotes)

---

## 🚀 PASSO A PASSO

### 1. Clonar Repositório
```bash
git clone https://github.com/seu-usuario/propzy.git
cd propzy
```

### 2. Instalar Dependências
```bash
# Instalar UV (se não tiver)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependências do projeto
uv sync
```

### 3. Configurar Banco de Dados

**Via Docker (recomendado):**
```bash
# Subir PostgreSQL + Redis
docker-compose up -d db redis

# Verificar
docker ps
```

**OU manualmente:**
```bash
# PostgreSQL
createdb propzy

# Redis
redis-server
```

### 4. Configurar .env
```bash
# Copiar template
cp .env.example .env

# Editar (opcional - padrões já funcionam)
nano .env
```

### 5. Migrations
```bash
# Aplicar migrations
python manage.py migrate

# Criar diretórios de mídia
mkdir -p media/logos media/heroes media/properties
```

### 6. Instalar Temas
```bash
# Instalar todos os temas
python manage.py install_themes

# Listar temas instalados
python manage.py install_themes --scan
```

### 7. Criar Superusuário
```bash
python manage.py createsuperuser

# Email: admin@propzy.local
# Senha: (senha forte)
```

### 8. Rodar Servidor
```bash
python manage.py runserver 0.0.0.0:8080
```

### 9. Acessar
```
Admin: http://localhost:8080/admin/
Login com credenciais criadas
```

---

## 🏡 CRIAR LANDING PAGE DE TESTE

1. **Acessar Admin:** http://localhost:8080/admin/

2. **Criar Landing Page:**
   - Landings → Landing Pages → Adicionar
   - Proprietário: admin
   - Subdomínio: `teste`
   - Nome do Negócio: "Imobiliária Teste"
   - Email: teste@teste.com
   - Tema: Modern Real Estate
   - ✅ Publicada
   - ✅ Ativa
   - Salvar

3. **Adicionar Imóveis:**
   - Landings → Imóveis → Adicionar
   - Landing Page: Imobiliária Teste
   - Preencher dados (título, tipo, preço, etc)
   - Upload de imagem
   - ✅ Ativo
   - Salvar

4. **Testar Localmente:**

**Opção A: Hosts file**
```bash
# Editar /etc/hosts (Linux/Mac)
sudo nano /etc/hosts

# Adicionar:
127.0.0.1 teste.propzy.local

# Acessar:
http://teste.propzy.local:8080
```

**Opção B: Parâmetro de teste**
```bash
# Abrir navegador:
http://localhost:8080/?__test__=teste
```

---

## 🔧 COMANDOS ÚTEIS

```bash
# Criar novo tema
python manage.py install_themes --scan

# Compilar traduções
python manage.py compilemessages

# Coletar estáticos
python manage.py collectstatic

# Criar usuário
python manage.py createsuperuser

# Shell interativo
python manage.py shell

# Verificar problemas
python manage.py check
```

---

## 📝 ESTRUTURA DO PROJETO

```
propzy/
├── apps/
│   ├── accounts/     # Usuários
│   ├── main/         # Dashboard
│   └── landings/     # Landing Pages ⭐
├── templates/
│   └── landings/
│       └── themes/   # Temas aqui
├── static/           # CSS/JS globais
├── media/            # Uploads
├── config/           # Settings
└── manage.py
```

---

## 🎨 DESENVOLVER NOVO TEMA

```bash
# 1. Criar estrutura
mkdir -p templates/landings/themes/meu-tema/static/css

# 2. Criar theme.json
cat > templates/landings/themes/meu-tema/theme.json << 'EOF'
{
  "name": "Meu Tema",
  "slug": "meu-tema",
  "version": "1.0.0",
  "description": "Descrição do tema",
  "category": "modern"
}
EOF

# 3. Criar index.html
# (copiar de outro tema e adaptar)

# 4. Instalar
python manage.py install_themes meu-tema
```

---

## 🐛 TROUBLESHOOTING

### Erro de conexão com banco
```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Ou
pg_isready
```

### Erro de conexão com Redis
```bash
# Verificar se Redis está rodando
docker ps | grep redis

# Ou
redis-cli ping
```

### Erro ao instalar temas
```bash
# Verificar estrutura
ls -la templates/landings/themes/

# Validar temas
python manage.py install_themes --validate
```

### Porta 8080 ocupada
```bash
# Usar outra porta
python manage.py runserver 0.0.0.0:8000
```

---

## 🧪 TESTES

```bash
# Rodar testes
python manage.py test

# Testes específicos
python manage.py test apps.landings

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 📚 PRÓXIMOS PASSOS

- **Deploy:** Leia `DEPLOY.md`
- **Arquitetura:** Leia `LANDINGS_README.md`
- **Segurança:** Leia `SECURITY_SUMMARY.md`

---

## ✅ CHECKLIST

- [ ] Dependências instaladas (`uv sync`)
- [ ] Banco criado e migrations aplicadas
- [ ] Temas instalados
- [ ] Superusuário criado
- [ ] Servidor rodando
- [ ] Admin acessível
- [ ] Landing page de teste criada
- [ ] Landing page funcionando

---

**Tempo:** ~5-10 minutos
**Dificuldade:** ⭐ (Muito Fácil)
**Resultado:** Sistema rodando localmente! 🎉

**BOM DESENVOLVIMENTO! 🚀**
