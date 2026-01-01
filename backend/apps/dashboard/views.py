from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404


@login_required
def dashboard(request):
    """Dashboard principal do tenant"""
    tenant = getattr(request, 'tenant', None)
    
    if not tenant:
        raise Http404
    
    # Verificar se usuário pertence ao tenant
    if request.user.tenant != tenant:
        raise Http404
    
    return render(request, 'dashboard/index.html', {
        'tenant': tenant,
    })



