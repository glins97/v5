from django.shortcuts import render
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Theme, Essay, Correction
from essay_manager.utils import get_view_by_permission, get_user_details
from django.utils.timezone import now
from functools import partial

@has_permission('student')
def student_dashboard_view(request):
    themes = Theme.objects.filter(start_date__lt=now(), end_date__gt=now())
    essays = Essay.objects.filter(user=request.user).order_by('-id')
    corrections = Correction.objects.filter(essay__user=request.user)
    themes_count = len(themes)
    essays_count = len(essays)
    corrections_count = len(corrections)
    completed_themes = 0
    
    done_corrections = 0
    active_corrections = 0
    unique_corrections = 0
    for theme in themes:
        if len(Essay.objects.filter(theme=theme, user=request.user).all()) > 0:
            completed_themes += 1

    for essay in essays:
        has_correction = False
        for correction in Correction.objects.filter(essay=essay):
            has_correction = True
            if correction.status == 'ACTIVE':
                active_corrections += 1
            elif correction.status == 'DONE':
                done_corrections += 1
        if has_correction:
            unique_corrections += 1

    data = {
        'title': 'Planejamento',
        'essays': list(essays)[-5:],
        'themes_count': themes_count,
        'essays_count': essays_count,
        'corrections_count': corrections_count,
        'user': get_user_details(request.user), 
        'registered': request.GET.get('registered', False),   
        'authed': request.GET.get('authed', False),   
    }

    if themes_count == completed_themes:
        data['themes_msg'] = 'Todos os temas concluídos'
        data['themes_icon'] = 'check'
        data['themes_card_type'] = 'success'
    else:
        data['themes_msg'] = '{} tema a fazer!'.format(themes_count - completed_themes)
        data['themes_icon'] = 'warning'
        data['themes_card_type'] = 'warning'

    if unique_corrections == essays_count:
        if active_corrections == 0:
            data['corrections_msg'] = 'Todas as correções concluídas'
            data['corrections_icon'] = 'check'
            data['corrections_card_type'] = 'success'
        else:
            data['corrections_msg'] = '{} em andamento!'.format(essays_count - active_corrections)
            data['corrections_icon'] = 'warning'
            data['corrections_card_type'] = 'warning'
    else:
        data['corrections_msg'] = '{} em espera'.format(essays_count - unique_corrections)
        data['corrections_icon'] = 'warning'
        data['corrections_card_type'] = 'warning'
         
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

