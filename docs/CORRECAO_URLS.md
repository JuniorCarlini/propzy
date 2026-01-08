# Correção de URLs - Namespaces

## Problema Identificado

Após a refatoração, os templates ainda referenciavam os namespaces antigos `main:` e `accounts:` que não existem mais na nova estrutura.

## Correções Realizadas

### 1. Namespace da Administração

**Antes:**
- `app_name = "administration"` em `apps/administration/urls.py`
- Templates referenciavam `main:` e `accounts:`

**Depois:**
- `app_name = "administration_panel"` em `apps/administration/urls.py`
- Todos os templates atualizados para `administration_panel:`

### 2. Arquivos Atualizados

#### Template Base (`templates/base.html`)
- `{% url 'main:index' %}` → `{% url 'administration_panel:dashboard' %}`
- `{% url 'main:toggle_theme' %}` → removido (funcionalidade descontinuada)
- `{% url 'accounts:user_list' %}` → `{% url 'administration_panel:user_list' %}`
- `{% url 'accounts:group_list' %}` → `{% url 'administration_panel:group_list' %}`
- `perms.accounts.view_user` → `perms.core.view_user`

#### Templates de Administração
- `templates/administration/dashboard.html`
- `templates/administration/user_list.html`
- `templates/administration/user_form.html`
- `templates/administration/user_confirm_delete.html`
- `templates/administration/group_list.html`
- `templates/administration/group_form.html`
- `templates/administration/group_confirm_delete.html`

Todas as referências `accounts:*` foram substituídas por `administration_panel:*`.

### 3. Permissões Atualizadas

Como o modelo `User` agora está em `apps.core`, as permissões também mudaram:
- `perms.accounts.view_user` → `perms.core.view_user`
- `perms.accounts.add_user` → `perms.core.add_user`

## URLs Disponíveis

### Namespace: `administration_panel`

- `administration_panel:dashboard` - Dashboard administrativo (raiz `/`)
- `administration_panel:dashboard_alt` - Dashboard alternativo (`/admin-panel/`)
- `administration_panel:user_list` - Lista de usuários
- `administration_panel:user_create` - Criar usuário
- `administration_panel:user_update` - Editar usuário
- `administration_panel:user_delete` - Excluir usuário
- `administration_panel:group_list` - Lista de grupos
- `administration_panel:group_create` - Criar grupo
- `administration_panel:group_update` - Editar grupo
- `administration_panel:group_delete` - Excluir grupo

### Outras URLs

- `admin/` - Django Admin (sem namespace)
- `accounts/*` - Allauth (namespace `account`)
- `landings/*` - Dashboard de landing pages (namespace `landings`)
- `/` (catch-all) - Landing pages públicas

## Funcionalidade de Dark Mode Restaurada

A funcionalidade de alternância de tema (dark mode) foi recriada no app `core`:

### Novos arquivos criados:
- `apps/core/views.py` - View `toggle_theme` para alternar tema do usuário
- `apps/core/urls.py` - URLs do app core

### Mudanças:
- Adicionado `path("core/", include("apps.core.urls"))` em `config/urls.py`
- Restaurado o botão de alternância no menu do usuário em `templates/base.html`

### Como usar:
Clique no avatar do usuário no canto superior direito e selecione "Modo escuro" ou "Modo claro".

## Status

✅ Sistema verificado sem erros
✅ Todos os namespaces corrigidos
✅ Permissões atualizadas
✅ Templates atualizados
✅ Dark mode restaurado e funcional

## Teste

Agora você pode acessar:

1. **http://localhost:8080/** - Será redirecionado para o dashboard administrativo (se autenticado)
2. **http://localhost:8080/admin-panel/** - Dashboard administrativo (alternativa)
3. **http://localhost:8080/accounts/login/** - Login
4. **http://localhost:8080/admin/** - Django Admin

Todos os links de navegação no sistema agora devem funcionar corretamente!

