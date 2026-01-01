"""
Backend de autenticação customizado para login por email.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Backend de autenticação que permite login usando email ao invés de username.
    O tenant é identificado automaticamente pelo middleware.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email', username)
        tenant = getattr(request, 'tenant', None)
        
        if not email or not password:
            return None
        
        # Se não houver tenant no request, não autenticar
        if not tenant:
            return None
        
        try:
            user = User.objects.get(email=email, tenant=tenant, is_active=True)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None



