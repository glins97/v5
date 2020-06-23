from django import template
register = template.Library()

@register.filter
def has_permission(obj, perm):
    """ 
    usage: {{ obj|has_permission:perm }}
    example: {{ user|has_permission:'student' }}
    """
    return obj.groups.filter(name=perm).exists()