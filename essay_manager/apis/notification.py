from django.shortcuts import redirect
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Notification
from django.http import HttpResponse
from datetime import datetime

import logging
logger = logging.getLogger('django')

@login_required
def read_all_notifications_endpoint(request):
    try:
        print(Notification.objects.filter(user=request.user, received=False))
        Notification.objects.filter(user=request.user, received=False).update(received=True)
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f'read_all_notifications_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return HttpResponse(status=500)