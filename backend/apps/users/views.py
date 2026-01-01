"""
Views para autenticação de usuários.
"""
from django.contrib.auth.views import LoginView
from django.contrib import messages


class CustomLoginView(LoginView):
    """View de login customizada que usa email ao invés de username."""
    template_name = 'users/login.html'
    
    def form_valid(self, form):
        """Override para usar email no lugar de username."""
        # O backend EmailBackend já trata email como username
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Override para mensagens de erro personalizadas."""
        messages.error(self.request, 'Email ou senha incorretos. Verifique suas credenciais.')
        return super().form_invalid(form)



