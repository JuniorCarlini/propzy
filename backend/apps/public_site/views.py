from django.shortcuts import render
from django.http import Http404


def landing_page(request):
    """Landing page do SaaS (propzy.com.br)"""
    # Verificar se é o domínio principal
    host = request.get_host().split(':')[0]
    if host not in ['propzy.com.br', 'www.propzy.com.br', 'localhost', '127.0.0.1']:
        raise Http404
    
    return render(request, 'public_site/landing.html')


def tenant_public_site(request):
    """Site público do tenant (cliente.propzy.com.br ou cliente.com.br)"""
    tenant = getattr(request, 'tenant', None)
    
    if not tenant:
        # Se não houver tenant, mostrar landing page
        return landing_page(request)
    
    return render(request, 'public_site/tenant_site.html', {
        'tenant': tenant,
    })

