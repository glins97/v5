from django.shortcuts import redirect
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Event
from django.http import JsonResponse

import logging
logger = logging.getLogger('django')

@login_required
def get_events_endpoint(request):
    try:
        return JsonResponse(
            [
                {
                    'title': event.title,
                    'year': event.year,
                    'month': event.month,
                    'day': event.day,
                } for event in Event.objects.filter(user=request.user)
            ],
        safe=False)
    except Exception as e:
        logger.error(f'get_events@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return JsonResponse([], safe=False)
        
@login_required
def create_event_endpoint(request):
    try:
        event = Event(user=request.user, title=request.POST['title'], year=request.POST['year'], month=request.POST['month'], day=request.POST['day'])
        event.save()
        return JsonResponse(
            {
                'title': event.title,
                'yeay': event.year,
                'month': event.month,
                'day': event.day,
            },
        safe=False)
    except Exception as e:
        logger.error(f'create_event@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return JsonResponse([], safe=False)

