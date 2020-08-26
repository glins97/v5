from django.shortcuts import render
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Theme, Essay, Correction, Event, Notification
from essay_manager.utils import get_view_by_permission, get_user_details
from django.utils.timezone import now
from functools import partial

@has_permission('student')
def student_dashboard_view(request):
    themes = Theme.objects.all()
    essays = Essay.objects.filter(user=request.user).order_by('-id')
    essays_count = essays.count()
    essays_msg = 'O trabalho duro vence talento!'

    grades = []
    correcting_essays_count = 0
    corrected_essays_count = 0
    for essay in essays:
        corrections = Correction.objects.filter(essay=essay, status='DONE')
        if corrections.count():
            corrected_essays_count += 1
            essay.correction_date = corrections.first().end_date.date
            grades.append(essay.grade)
        else: 
            correcting_essays_count += 1
            essay.correction_date = '-'
            essay.grade = '-'

    correcting_essays_icon = 'warning'
    correcting_essays_card_type = 'warning'
    correcting_essays_msg = 'Aguarde a correção nos próximos dias!'
    if correcting_essays_count == 0:
        correcting_essays_icon = 'check'
        correcting_essays_card_type = 'success'
        correcting_essays_msg = 'Todas as redações foram corrigidas'

    corrected_essays_icon = 'warning'
    corrected_essays_card_type = 'warning'
    corrected_essays_msg = 'Redação é método.'
    if corrected_essays_count == essays_count:
        corrected_essays_icon = 'check'
        corrected_essays_card_type = 'success'
        corrected_essays_msg = 'Busque outros temas!'

    theme_enem = Theme.objects.filter(active=True, jury='ENEM', highlighted_start_date__lt=now(), highlighted_end_date__gt=now()).first()
    if theme_enem:
        theme_enem.done = False
        if Essay.objects.filter(user=request.user, theme=theme_enem).count():
            theme_enem.done = True

    theme_vunesp = Theme.objects.filter(active=True, jury='VUNESP', highlighted_start_date__lt=now(), highlighted_end_date__gt=now()).first()
    if theme_vunesp:
        theme_vunesp.done = False
        if Essay.objects.filter(user=request.user, theme=theme_vunesp).count():
            theme_vunesp.done = True

    data = {
        'title': 'Preparação',
        
        'user': get_user_details(request.user), 
        'registered': request.GET.get('registered', False),   
        'authed': request.GET.get('authed', False),   
        
        'events': Event.objects.filter(user=request.user), 
        'theme_enem': theme_enem,
        'theme_vunesp': theme_vunesp,

        'grades': str(grades[::-1]),
        'essays': list(essays)[-5:],
        'essays_count': essays_count,
        'essays_msg': essays_msg,

        'correcting_essays_count': correcting_essays_count,
        'correcting_essays_icon': correcting_essays_icon,
        'correcting_essays_card_type': correcting_essays_card_type,
        'correcting_essays_msg': correcting_essays_msg,

        'corrected_essays_count': corrected_essays_count,
        'corrected_essays_icon': corrected_essays_icon,
        'corrected_essays_card_type': corrected_essays_card_type,
        'corrected_essays_msg': corrected_essays_msg,
    }
         
    return render(request, 'dashboard/student.html', data)

@has_permission('monitor')
def monitor_dashboard_view(request):
    corrections = list(Correction.objects.filter(user=request.user).order_by('-id').order_by('status'))
    essays = Essay.objects.filter().order_by('id')
    
    uncorrected_essays = []
    for essay in essays:
        if not Correction.objects.filter(essay=essay).count():
            uncorrected_essays.append(essay)
    uncorrected_essays_count = len(uncorrected_essays)

    active_corrections = Correction.objects.filter(user=request.user, status='ACTIVE')
    active_corrections_count = active_corrections.count()
    done_corrections = Correction.objects.filter(user=request.user, status='DONE')
    done_corrections_count = done_corrections.count()

    data = {
        'title': 'Inicial',
        'corrections': corrections[:5],
        'done_corrections': list(done_corrections),
        'done_corrections_count': done_corrections_count,
        'uncorrected_essays': uncorrected_essays[:5],
        'uncorrected_essays_count': uncorrected_essays_count,
        'active_corrections_count': active_corrections_count,
        'user': get_user_details(request.user),    
    }

    if uncorrected_essays_count == 0:
        data['uncorrected_essays_msg'] = 'Todos as redações foram corrigidas'
        data['uncorrected_essays_icon'] = 'check'
        data['uncorrected_essays_card_type'] = 'success'
    else:
        data['uncorrected_essays_msg'] = '{} redações a corrigir!'.format(len(uncorrected_essays))
        data['uncorrected_essays_icon'] = 'warning'
        data['uncorrected_essays_card_type'] = 'warning'        

    if active_corrections_count == 0:
        data['active_corrections_msg'] = 'Sem correções ativas'
        data['active_corrections_icon'] = 'check'
        data['active_corrections_card_type'] = 'success'
    else:
        if active_corrections_count == 1:
            data['active_corrections_msg'] = '1 correção ativa'
        else:
            data['active_corrections_msg'] = '{} correções ativas'.format(active_corrections_count)
        data['active_corrections_icon'] = 'warning'
        data['active_corrections_card_type'] = 'warning'      
    
    return render(request, 'dashboard/monitor.html', data)

def dashboard_view(request):
    return get_view_by_permission(request, **{
        'student': student_dashboard_view,
        'monitor': monitor_dashboard_view,
    })

