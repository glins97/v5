from django.http import HttpResponse, HttpResponseNotFound
from essay_manager.decorators import login_required
from essay_manager.models import Essay
from bauth.views import e403_view, e500_view

import os.path
import mimetypes

@login_required
def get_essay_file(request, url):
    if 'uploads/' not in url:
        url = 'uploads/' + url
        
    mimetypes.init()
    try:
        matched = request.user.groups.filter(name='monitor').exists()
        essays = Essay.objects.filter(user=request.user)
        for essay in essays:
            if essay.file == url:
                matched = True
        if not matched: return e403_view(request)

        fsock = open(url, "rb")
        file_name = os.path.basename(url) 
        mime_type_guess = mimetypes.guess_type(file_name)
        if mime_type_guess is not None:
            response = HttpResponse(fsock, content_type=mime_type_guess[0])
        response['Content-Disposition'] = 'attachment; filename=' + file_name            
    except IOError:
        response = e500_view(request)
    return response

@login_required
def get_view_by_permission(request, *args, **kwargs):
    for key in kwargs:
        if request.user.groups.filter(name=key).exists():
            return kwargs[key](request, *args)
    return kwargs.get('default', e403_view(request))

def get_user_details(user):
    full_name = ''
    initials = ''
    if user.first_name:
        print('user.first_name', user.first_name)
        initials += user.first_name[0] 
        full_name += user.first_name
    if user.last_name:
        initials += user.last_name[0]
        full_name += user.last_name
    if not full_name:
        full_name = 'Aluno'
        initials = 'A'
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': full_name,
        'initials': initials,
        'obj': user,
    }