import itertools
from django import template
register = template.Library()

@register.filter
def chunks(value, chunk_length):
    clen = int(chunk_length)
    i = iter(value)
    while True:
        chunk = list(itertools.islice(i, clen))
        if chunk:
            yield chunk
        else:
            break