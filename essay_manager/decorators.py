from django.shortcuts import redirect
from bauth.views import login_view
from bauth.views import e403_view
from django.views.decorators.csrf import csrf_exempt


import logging
logger = logging.getLogger('django')

@csrf_exempt
def login_required(f, *args, **kwargs):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return f(request, *args, **kwargs)
        else:
            logger.info(f'login_required@decorators::Unauthorized user | {request.user} {request}')
            return login_view(request)
    return wrapper

def has_permission(perm, *args, **kwargs):
    def has_permission_(f, *args, **kwargs):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name=perm).exists() or request.user.groups.filter(name='superuser').exists():
                return f(request, *args, **kwargs)
            else:
                return e403_view(request, *args, **kwargs)
        return wrapper
    return has_permission_
