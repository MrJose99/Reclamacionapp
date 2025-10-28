from django import template
import uuid

register = template.Library()

@register.filter
def safe_uuid(value):
    """
    Convierte de forma segura un valor a string,
    manejando UUIDs y otros tipos
    """
    try:
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)
    except:
        return "N/A"

@register.filter
def truncate_uuid(value, chars=8):
    """
    Trunca un UUID para mostrarlo de forma más corta
    """
    try:
        uuid_str = str(value)
        return f"{uuid_str[:chars]}..."
    except:
        return "N/A"