from django.shortcuts import render
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Essay, Correction, ErrorClassification, GenericErrorClassification 
from essay_manager.utils import get_view_by_permission, get_user_details
from bauth.views import e403_view
from django.shortcuts import redirect
from django.utils.html import mark_safe

@has_permission('student')
@login_required
def _student_essays_view(request):
    essays = Essay.objects.filter(user=request.user).order_by('-id')
    for essay in essays:
        if Correction.objects.filter(essay=essay, status='DONE').count() == 0:
            essay.grade = '-'
    data = {
        'title': 'Redações',
        'added': request.GET.get('added', 'None'),
        'essays': essays,
        'user': get_user_details(request.user),
    }
    return render(request, 'essays/student.html', dict(data, **{key:request.GET[key] for key in request.GET}))

def get_verbose_mode(mode):
    return {
        '1': 'Jornada 1',
        '2': 'Jornada 2',
        '3': 'Jornada 3',
    }.get(mode, '-')

@has_permission('monitor')
@login_required
def _monitor_essays_view(request):
    data = {
        'title': 'Redações',
        'added': request.GET.get('added', 'None'),
        'mailed': request.GET.get('mailed', 'None'),
        'user': get_user_details(request.user),
        'uncorrected_essays_count': Essay.objects.filter(correction__isnull=True).count(),
        'active_corrections_essays_count': Essay.objects.filter(correction__status='ACTIVE').count(),
        'done_corrections_count': Essay.objects.filter(correction__status='DONE').count(),
        'created': request.GET.get('created', None),
        'updated': request.GET.get('updated', None),
    }
    return render(request, 'essays/monitor.html', data)

@has_permission('student')
@login_required
def _student_essay_view(request, id):
    corrections = Correction.objects.filter(essay=id)
    essay = Essay.objects.get(id=id)
    if essay.user != request.user:
        return e403_view(request)
        
    first_name = essay.user.first_name.split()[0]
    data = {
        'title': 'Redações',
        'essay': essay,
        'user': get_user_details(request.user),
        'username': first_name[0].upper() + first_name[1:].lower(), 
        'data': mark_safe(corrections[0].data) if corrections else {},
    }
    if essay.theme.jury == 'VUNESP':
        return render(request, 'essay/student/vunesp.html', data)
    return render(request, 'essay/student/enem.html', data)

def add_padding(l, chunk_size, padding):
    while len(l) % chunk_size != 0:
        l.append(padding)
    return l

def wrap_errors(e):
    return add_padding(e, 3, mark_safe(""" <div class="form-check col-sm"> </div> """))

@has_permission('monitor')
@login_required
def _monitor_essay_view(request, id):
    corrections = Correction.objects.filter(essay=id)
    if not corrections.count():
        return redirect(f'/corrections/new/{id}/')

    essay = Essay.objects.get(id=id)
    first_name = essay.user.first_name.split()[0]
    data = {
        'title': 'Redações',
        'essay': essay,
        'user': get_user_details(request.user),
        'username': first_name[0].upper() + first_name[1:].lower(), 
        'created': request.GET.get('created', None),
        'data': mark_safe(corrections[0].data),
    }
    if essay.theme.jury == 'ENEM':
        data['error_classifications_c1'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='1')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c2'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='2')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c3'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='3')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c4'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='4')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c5'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='5')), key=lambda e: int(e.code)) if o.parent is None])

        data['generic_error_classifications_c1'] = wrap_errors([o.get_html() for o in sorted(list(GenericErrorClassification.objects.filter(competency='1')), key=lambda e: int(e.code)) if o.parent is None])
        data['generic_error_classifications_c2'] = wrap_errors([o.get_html() for o in sorted(list(GenericErrorClassification.objects.filter(competency='2')), key=lambda e: int(e.code)) if o.parent is None])
        data['generic_error_classifications_c3'] = wrap_errors([o.get_html() for o in sorted(list(GenericErrorClassification.objects.filter(competency='3')), key=lambda e: int(e.code)) if o.parent is None])
        data['generic_error_classifications_c4'] = wrap_errors([o.get_html() for o in sorted(list(GenericErrorClassification.objects.filter(competency='4')), key=lambda e: int(e.code)) if o.parent is None])
        data['generic_error_classifications_c5'] = wrap_errors([o.get_html() for o in sorted(list(GenericErrorClassification.objects.filter(competency='5')), key=lambda e: int(e.code)) if o.parent is None])

        data['error_classifications_g0'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='0', jury='ENEM')), key=lambda e: int(e.code)) if o.parent is None])
        return render(request, 'essay/monitor/enem.html', data)
    
    elif essay.theme.jury == 'VUNESP':
        data['error_classifications_c1'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='1')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c2'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='2')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c3'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='3')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c4'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='4')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c5'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='5')), key=lambda e: int(e.code)) if o.parent is None])

        data['generic_error_classifications_ca'] = wrap_errors([o.get_html() for o in sorted(list(GenericErrorClassification.objects.filter(competency='a')), key=lambda e: int(e.code)) if o.parent is None])
        data['generic_error_classifications_cb'] = wrap_errors([o.get_html() for o in sorted(list(GenericErrorClassification.objects.filter(competency='b')), key=lambda e: int(e.code)) if o.parent is None])
        data['generic_error_classifications_cc'] = wrap_errors([o.get_html() for o in sorted(list(GenericErrorClassification.objects.filter(competency='c')), key=lambda e: int(e.code)) if o.parent is None])

        data['error_classifications_g0'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='0', jury='VUNESP')), key=lambda e: int(e.code)) if o.parent is None])
        return render(request, 'essay/monitor/vunesp.html', data)
    
    elif essay.theme.jury == 'CESPE':
        data['error_classifications_c1'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='1')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c2'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='2')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c3'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='3')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c4'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='4')), key=lambda e: int(e.code)) if o.parent is None])
        data['error_classifications_c5'] = wrap_errors([o.get_html() for o in sorted(list(ErrorClassification.objects.filter(competency='5')), key=lambda e: int(e.code)) if o.parent is None])

        return render(request, 'essay/monitor/cespe.html', data)
    
    return redirect('/essays/')

def essays_view(request):
    return get_view_by_permission(request, **{
        'student': _student_essays_view,
        'monitor': _monitor_essays_view,
    })

def essay_view(request, id):
    return get_view_by_permission(request, id, **{
        'student': _student_essay_view,
        'monitor': _monitor_essay_view,
    })


