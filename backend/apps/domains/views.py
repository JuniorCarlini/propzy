"""
Views para gerenciamento de domínios no dashboard.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Domain
from .tasks import verify_domain
from apps.tenants.models import Tenant


@login_required
def domain_list(request):
    """Lista domínios do tenant"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        raise Http404
    
    # Verificar se usuário pertence ao tenant
    if request.user.tenant != tenant:
        raise Http404
    
    domains = Domain.objects.filter(tenant=tenant)
    return render(request, 'domains/list.html', {
        'domains': domains,
        'tenant': tenant,
    })


@login_required
def domain_create(request):
    """Criar novo domínio"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        raise Http404
    
    if request.user.tenant != tenant:
        raise Http404
    
    if request.method == 'POST':
        domain_name = request.POST.get('domain', '').strip().lower()
        domain_type = request.POST.get('type', 'custom')
        
        if not domain_name:
            messages.error(request, 'Nome do domínio é obrigatório')
            return redirect('domains:create')
        
        # Criar domínio
        domain = Domain.objects.create(
            tenant=tenant,
            domain=domain_name,
            type=domain_type,
            is_verified=False,
        )
        
        messages.success(request, f'Domínio {domain_name} cadastrado! Configure o DNS conforme instruções.')
        
        # Iniciar verificação
        verify_domain.delay(str(domain.id))
        
        return redirect('domains:detail', domain_id=str(domain.id))
    
    return render(request, 'domains/create.html', {
        'tenant': tenant,
    })


@login_required
def domain_detail(request, domain_id):
    """Detalhes do domínio com instruções DNS"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        raise Http404
    
    domain = get_object_or_404(Domain, id=domain_id, tenant=tenant)
    
    # Verificar se usuário pertence ao tenant
    if request.user.tenant != tenant:
        raise Http404
    
    # Obter IP do servidor (pode ser configurado via settings)
    from django.conf import settings
    server_ip = getattr(settings, 'VPS_IP', 'SEU_IP_VPS')
    proxy_domain = getattr(settings, 'PROXY_DOMAIN', 'proxy.propzy.com.br')
    
    # Instruções DNS
    dns_instructions = {
        'cname': {
            'type': 'CNAME',
            'name': '@',
            'destination': proxy_domain,
            'ttl': 'Auto',
        },
        'a_record': {
            'type': 'A',
            'name': '@',
            'destination': server_ip,
            'ttl': 'Auto',
        },
    }
    
    return render(request, 'domains/detail.html', {
        'domain': domain,
        'tenant': tenant,
        'dns_instructions': dns_instructions,
        'server_ip': server_ip,
        'proxy_domain': proxy_domain,
    })


@login_required
def domain_verify(request, domain_id):
    """Forçar verificação de domínio"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        raise Http404
    
    domain = get_object_or_404(Domain, id=domain_id, tenant=tenant)
    
    if request.user.tenant != tenant:
        raise Http404
    
    # Iniciar verificação
    verify_domain.delay(str(domain.id))
    
    messages.info(request, f'Verificação do domínio {domain.domain} iniciada. Aguarde alguns minutos.')
    
    return redirect('domains:detail', domain_id=str(domain.id))



