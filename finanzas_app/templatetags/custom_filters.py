from django import template

register = template.Library()


@register.filter
def dict_key(dictionary, key):
    """Obtiene un valor de un diccionario usando una clave variable"""
    return dictionary.get(key)
