from django.contrib import admin
from .models import Domain
from .tasks import verify_domain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'type', 'is_verified', 'verified_at', 'created_at']
    list_filter = ['type', 'is_verified', 'created_at']
    search_fields = ['domain', 'tenant__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'verified_at']
    raw_id_fields = ['tenant']
    actions = ['verify_selected_domains']
    
    def verify_selected_domains(self, request, queryset):
        """Ação para verificar domínios selecionados"""
        for domain in queryset:
            verify_domain.delay(str(domain.id))
        self.message_user(request, f'{queryset.count()} domínio(s) enviado(s) para verificação.')
    verify_selected_domains.short_description = 'Verificar domínios selecionados'
