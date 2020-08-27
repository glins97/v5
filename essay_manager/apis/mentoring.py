from django.shortcuts import redirect
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Mentoring
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.models import User

from django.contrib.auth import login as login_
from django.contrib.auth import logout as logout_

import logging
logger = logging.getLogger('django')

@has_permission('monitor')
def start_mentoring_endpoint(request, id):
    try:
        mentoring = Mentoring.objects.filter(student=User.objects.get(id=id), mentor=request.user).first()
        if mentoring:
            mentoring.active = True
            mentoring.save()
        else:
            Mentoring(student=User.objects.get(id=id), mentor=request.user, active=True).save()
        return redirect('/mentoring/')
    except Exception as e:
        logger.error(f'start_mentoring_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return redirect('/mentoring/')

@login_required
@has_permission('monitor')
def finish_mentoring_endpoint(request, id):
    try:
        mentoring = Mentoring.objects.filter(student=User.objects.get(id=id), mentor=request.user).first()
        if mentoring:
            mentoring.active = False
            mentoring.save()
        return redirect('/mentoring/')
    except Exception as e:
        logger.error(f'finish_mentoring_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return redirect('/mentoring/')
        
@has_permission('monitor')
def access_as_endpoint(request, id):
    try:
        user = User.objects.get(id=id)
        if user:
            logout_(request)
            login_(request, user)
        return redirect('/')
    except Exception as e:
        logger.error(f'access_as_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return redirect('/mentoring/')