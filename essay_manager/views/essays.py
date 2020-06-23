from django.shortcuts import render
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Essay, Correction, ErrorClassification
from essay_manager.utils import get_view_by_permission, get_user_details
from essay_manager.views.errors import e403_view
from django.shortcuts import redirect
from django.utils.html import mark_safe

@has_permission('student')
@login_required
def _student_essays_view(request):
    data = {
        'title': 'Redações',
        'added': request.GET.get('added', 'None'),
        'essays': Essay.objects.filter(user=request.user).order_by('-id'),
        'user': get_user_details(request.user),
    }
    return render(request, 'essays/student.html', dict(data, **{key:request.GET[0] for key in request.GET}))

@has_permission('monitor')
@login_required
def _monitor_essays_view(request):
    active_correction_essays = [essay for essay in Essay.objects.filter().order_by('id') if Correction.objects.filter(essay=essay, status='ACTIVE')]
    for index, essay in enumerate(active_correction_essays):
        active_correction_essays[index].monitor = Correction.objects.filter(essay=essay, status='ACTIVE').get().user

    done_correction_essays = [essay for essay in Essay.objects.filter().order_by('-id') if Correction.objects.filter(essay=essay, status='DONE')]
    for index, essay in enumerate(done_correction_essays):
        done_correction_essays[index].monitor = Correction.objects.filter(essay=essay, status='DONE').get().user

    data = {
        'title': 'Redações',
        'added': request.GET.get('added', 'None'),
        'mailed': request.GET.get('mailed', 'None'),
        'essays': [essay for essay in Essay.objects.filter().order_by('id') if Correction.objects.filter(essay=essay).count() == 0],
        'active_correction_essays': active_correction_essays,
        'done_correction_essays': done_correction_essays[:10],
        'user': get_user_details(request.user),
        'created': request.GET.get('created', None),
        'updated': request.GET.get('updated', None),
    }
    return render(request, 'essays/monitor.html', data)

@has_permission('student')
@login_required
def _student_essay_view(request, id):
    essay = Essay.objects.get(id=id)
    if essay.user != request.user:
        return e403_view(request)
        
    data = {
        'title': 'Redações',
        'essay': essay,
        'user': get_user_details(request.user),
    }
    return render(request, 'essay/student.html', data)

@has_permission('monitor')
@login_required
def _monitor_essay_view(request, id):
    corrections = Correction.objects.filter(essay=id)
    if not corrections.count():
        return redirect(f'/corrections/new/{id}/')
    print('corrections[0].data', corrections[0].data)

    error_classifications_c1 = [o.get_html() for o in ErrorClassification.objects.filter(competency='1') if o.parent is None]
    error_classifications_c2 = [o.get_html() for o in ErrorClassification.objects.filter(competency='2') if o.parent is None]
    error_classifications_c3 = [o.get_html() for o in ErrorClassification.objects.filter(competency='3') if o.parent is None]
    error_classifications_c4 = [o.get_html() for o in ErrorClassification.objects.filter(competency='4') if o.parent is None]
    error_classifications_c5 = [o.get_html() for o in ErrorClassification.objects.filter(competency='5') if o.parent is None]
    data = {
        'title': 'Redações',
        'essay': Essay.objects.get(id=id),
        'user': get_user_details(request.user),
        'created': request.GET.get('created', None),
        'error_classifications_c1': error_classifications_c1,
        'error_classifications_c2': error_classifications_c2,
        'error_classifications_c3': error_classifications_c3,
        'error_classifications_c4': error_classifications_c4,
        'error_classifications_c5': error_classifications_c5,
        'data': mark_safe(corrections[0].data),
    }
    return render(request, 'essay/monitor.html', data)

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


