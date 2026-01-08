"""
Template tags para propriedades
"""
from django import template

register = template.Library()


@register.filter
def format_price(value):
    """Formata um preço decimal para exibição brasileira"""
    if not value:
        return ""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")










