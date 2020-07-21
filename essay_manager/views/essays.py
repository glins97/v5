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
    data = {
        'title': 'Redações',
        'added': request.GET.get('added', 'None'),
        'essays': Essay.objects.filter(user=request.user).order_by('-id'),
        'user': get_user_details(request.user),
    }
    return render(request, 'essays/student.html', dict(data, **{key:request.GET[key] for key in request.GET}))

@has_permission('monitor')
@login_required
def _monitor_essays_view(request):
    essays = Essay.objects.filter().order_by('id')
    uncorrected_essays = []
    for essay in essays:
        if not Correction.objects.filter(essay=essay).count():
            uncorrected_essays.append(essay)
    uncorrected_essays_count = len(uncorrected_essays)

    active_correction_essays = [essay for essay in Essay.objects.filter().order_by('id') if Correction.objects.filter(essay=essay, status='ACTIVE')]
    for index, essay in enumerate(active_correction_essays):
        active_correction_essays[index].monitor = Correction.objects.filter(essay=essay, status='ACTIVE').get().user
    active_corrections_essays_count = len(active_correction_essays)

    done_correction_essays = sorted(
        [essay for essay in Essay.objects.filter() if Correction.objects.filter(essay=essay, status='DONE').count()],
        key=lambda essay: (Correction.objects.filter(essay=essay, status='DONE').first().end_date, Correction.objects.filter(essay=essay, status='DONE').first().id),
        reverse=True)
    for index, essay in enumerate(done_correction_essays):
        done_correction_essays[index].monitor = Correction.objects.filter(essay=essay, status='DONE').get().user
    done_corrections_count = len(done_correction_essays)

    data = {
        'title': 'Redações',
        'added': request.GET.get('added', 'None'),
        'mailed': request.GET.get('mailed', 'None'),
        'essays': [essay for essay in Essay.objects.filter().order_by('id') if Correction.objects.filter(essay=essay).count() == 0],
        'active_correction_essays': active_correction_essays,
        'done_correction_essays': done_correction_essays[:10],

        'done_corrections_count': done_corrections_count,
        'active_corrections_essays_count': active_corrections_essays_count,
        'uncorrected_essays_count': uncorrected_essays_count,
        
        'active_corrections_essays_card_type': 'success' if active_corrections_essays_count == 0 else 'warning',
        'active_corrections_essays_icon': 'check' if active_corrections_essays_count == 0 else 'warning',
        'uncorrected_essays_card_type': 'success' if uncorrected_essays_count == 0 else 'warning',
        'uncorrected_essays_icon': 'check' if uncorrected_essays_count == 0 else 'warning',

        'user': get_user_details(request.user),
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
    return render(request, 'essay/student.html', data)

def add_padding(l, chunk_size, padding):
    while len(l) % chunk_size != 0:
        l.append(padding)
    return l

@has_permission('monitor')
@login_required
def _monitor_essay_view(request, id):
    corrections = Correction.objects.filter(essay=id)
    if not corrections.count():
        return redirect(f'/corrections/new/{id}/')

    error_classifications_c1 = [o.get_html() for o in ErrorClassification.objects.filter(competency='1').order_by('code') if o.parent is None]
    error_classifications_c2 = [o.get_html() for o in ErrorClassification.objects.filter(competency='2').order_by('code') if o.parent is None]
    error_classifications_c3 = [o.get_html() for o in ErrorClassification.objects.filter(competency='3').order_by('code') if o.parent is None]
    error_classifications_c4 = [o.get_html() for o in ErrorClassification.objects.filter(competency='4').order_by('code') if o.parent is None]
    error_classifications_c5 = [o.get_html() for o in ErrorClassification.objects.filter(competency='5').order_by('code') if o.parent is None]

    generic_error_classifications_c1 = [o.get_html() for o in GenericErrorClassification.objects.filter(competency='1').order_by('code') if o.parent is None]
    generic_error_classifications_c2 = [o.get_html() for o in GenericErrorClassification.objects.filter(competency='2').order_by('code') if o.parent is None]
    generic_error_classifications_c3 = [o.get_html() for o in GenericErrorClassification.objects.filter(competency='3').order_by('code') if o.parent is None]
    generic_error_classifications_c4 = [o.get_html() for o in GenericErrorClassification.objects.filter(competency='4').order_by('code') if o.parent is None]
    generic_error_classifications_c5 = [o.get_html() for o in GenericErrorClassification.objects.filter(competency='5').order_by('code') if o.parent is None]

    error_classifications_g0 = sorted([o.get_html() for o in ErrorClassification.objects.filter(competency='0').order_by('code') if o.parent is None], key=lambda item: str(item))
    essay = Essay.objects.get(id=id)
    first_name = essay.user.first_name.split()[0]
    data = {
        'title': 'Redações',
        'essay': essay,
        'user': get_user_details(request.user),
        'username': first_name[0].upper() + first_name[1:].lower(), 
        'created': request.GET.get('created', None),
        'error_classifications_c1': add_padding(error_classifications_c1, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'error_classifications_c2': add_padding(error_classifications_c2, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'error_classifications_c3': add_padding(error_classifications_c3, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'error_classifications_c4': add_padding(error_classifications_c4, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'error_classifications_c5': add_padding(error_classifications_c5, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'error_classifications_g0': add_padding(error_classifications_g0, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),

        'generic_error_classifications_c1': add_padding(generic_error_classifications_c1, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'generic_error_classifications_c2': add_padding(generic_error_classifications_c2, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'generic_error_classifications_c3': add_padding(generic_error_classifications_c3, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'generic_error_classifications_c4': add_padding(generic_error_classifications_c4, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
        'generic_error_classifications_c5': add_padding(generic_error_classifications_c5, 3, mark_safe(""" <div class="form-check col-sm"> </div> """)),
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


