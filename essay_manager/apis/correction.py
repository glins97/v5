from essay_manager.decorators import login_required, has_permission
from django.shortcuts import redirect
from essay_manager.models import Correction, Essay
import logging
import json 

import logging
logger = logging.getLogger('django')

@has_permission('monitor')
@login_required
def create_correction_endpoint(request, id):
    try:
        if Correction.objects.filter(user=request.user, essay__id=id).count() == 0:
            Correction(user=request.user, essay=Essay.objects.get(id=id), data='{}').save()
        return redirect('/essays/{}/?created=True'.format(id))
    except Exception as e:
        logger.error(f'create_correction_endpoint@correction::Exception thrown | {request.user} {request} {id} {repr(e)}')
        return redirect('/essays/?created=False')
        
@has_permission('monitor')
@login_required
def update_correction_endpoint(request, id):
    try:
        essay = Essay.objects.get(id=id)
        correction = Correction.objects.get(user=request.user, essay=essay)
        for attr in request.POST:
            setattr(correction, attr, request.POST[attr])
        correction.save()
        return redirect('/essays/?updated=True')
    except Exception as e:
        logger.error(f'create_correction_endpoint@correction::Exception thrown | {request.user} {request} {id} {repr(e)}')
        return redirect('/essays/{}/?updated=False'.format(id))