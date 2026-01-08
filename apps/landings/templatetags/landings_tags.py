"""
Template tags para landings
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Retorna um item de um dicionário usando uma chave"""
    if dictionary is None:
        return None
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.simple_tag
def section_enabled(site, section_key):
    """Verifica se uma seção está habilitada"""
    try:
        config = site.theme_config
        return config.is_section_enabled(section_key)
    except:
        return True  # Por padrão, todas as seções estão habilitadas


@register.simple_tag
def section_config(site, section_key):
    """Retorna as configurações de uma seção"""
    try:
        config = site.theme_config
        section_data = config.get_section_config(section_key)
        # Garantir que sempre retorna um dict
        return section_data if isinstance(section_data, dict) else {}
    except:
        return {}


@register.simple_tag
def get_filtered_properties(site, section_config):
    """
    Retorna propriedades filtradas baseado na configuração da seção.
    Otimizado com prefetch_related para melhor desempenho.
    """
    from apps.properties.models import Property

    # Query base otimizada
    properties = site.properties.filter(is_active=True).prefetch_related("images").order_by("-created_at")

    # Aplicar filtros da configuração
    if section_config.get("show_featured_only"):
        properties = properties.filter(is_featured=True)

    if section_config.get("filter_transaction"):
        transaction = section_config["filter_transaction"]
        if transaction in ["sale", "rent"]:
            properties = properties.filter(transaction_type=transaction)
        # "both" não precisa de filtro

    if section_config.get("filter_type"):
        properties = properties.filter(property_type=section_config["filter_type"])

    if section_config.get("filter_city"):
        properties = properties.filter(city__icontains=section_config["filter_city"])

    # Aplicar limite
    limit = section_config.get("limit", 0)
    if limit and limit > 0:
        properties = properties[:limit]

    return properties

