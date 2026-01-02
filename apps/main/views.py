from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index_view(request):
    """Renderiza a página inicial."""

    return render(request, "main/index.html")
