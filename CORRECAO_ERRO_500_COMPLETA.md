# ✅ Correção do Erro 500 - COMPLETA

## 🎯 Problema Identificado

Após resetar o banco de dados, o erro 500 na página de login (`/accounts/login/`) era causado por:

**O Site do Django (`django.contrib.sites`) estava configurado como `example.com` em vez de `propzy.com.br`**

O `django-allauth` precisa que o `SITE_ID` corresponda ao domínio correto do sistema.

---

## ✅ SOLUÇÃO APLICADA

### 1. Site do Django Corrigido

```bash
# Executei este comando para corrigir:
python manage.py shell -c "
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'propzy.com.br'
site.name = 'Propzy'
site.save()
"
```

### 2. Comando Criado para Futuro

Criei o comando `setup_site` para configurar automaticamente:

```bash
python manage.py setup_site
```

Este comando:
- Verifica se o Site ID 1 está configurado corretamente
- Atualiza o domínio se necessário
- Cria o Site se não existir

---

## 🔧 COMANDOS PARA APÓS RESET DO BANCO

Sempre que resetar o banco, execute estes comandos em ordem:

```bash
# 1. Aplicar migrações
python manage.py migrate

# 2. Configurar Site do Django (NOVO!)
python manage.py setup_site

# 3. Instalar temas (se necessário)
python manage.py install_themes

# 4. Criar superusuário (se necessário)
python manage.py createsuperuser

# 5. Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

---

## ✅ VERIFICAÇÃO

Após corrigir, verifique:

```bash
# Verificar Site do Django
python manage.py shell -c "
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
print(f'Site ID {site.id}: {site.domain} ({site.name})')
"

# Deve mostrar:
# Site ID 1: propzy.com.br (Propzy)
```

---

## 🎉 RESULTADO

Agora a página de login deve funcionar corretamente!

Acesse: `http://propzy.com.br/accounts/login/`

---

## 📝 NOTAS

- O `SITE_ID = 1` no `settings.py` deve corresponder ao Site no banco
- Após reset do banco, sempre execute `python manage.py setup_site`
- O comando `setup_site` usa `BASE_DOMAIN` do settings ou padrão `propzy.com.br`



