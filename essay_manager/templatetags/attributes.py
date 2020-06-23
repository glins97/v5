from django import template
register = template.Library()

@register.filter
def attr(obj, attr_):
    """ 
    usage: {{ obj|attr:attr_name }}
    example: {{ user|attr:name }} -> equals user.name
    """
    return getattr(obj, attr_)