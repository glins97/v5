from django.shortcuts import render
from django.utils.timezone import now
from essay_manager.decorators import login_required
from essay_manager.models import Theme, Essay
from essay_manager.utils import get_user_details

@login_required
def themes_view(request):
    themes = []
    axes = {}
    axes_enem = {}
    axes_vunesp = {}
    axes_cespe = {}
    for theme in Theme.objects.filter(active=True):
        if theme.axis not in axes:
            axes[theme.axis] = {
                'description': theme.axis, 
                'total_themes': 1, 
                'done_themes': 0, 
            }
            if theme.jury == 'ENEM':
                axes_enem[theme.axis] = {
                    'description': theme.axis, 
                    'total_themes': 1, 
                    'done_themes': 0, 
                }
            elif theme.jury == 'VUNESP':
                axes_vunesp[theme.axis] = {
                    'description': theme.axis, 
                    'total_themes': 1, 
                    'done_themes': 0, 
                }
            elif theme.jury == 'CESPE':
                axes_cespe[theme.axis] = {
                    'description': theme.axis, 
                    'total_themes': 1, 
                    'done_themes': 0, 
                }
        else:
            axes[theme.axis]['total_themes'] += 1
            if theme.jury == 'ENEM':
               axes_enem[theme.axis]['total_themes'] += 1
            elif theme.jury == 'VUNESP':
               axes_vunesp[theme.axis]['total_themes'] += 1
            elif theme.jury == 'CESPE':
               axes_cespe[theme.axis]['total_themes'] += 1

        theme.last_essay = '-'
        theme.done_essays = Essay.objects.filter(theme=theme, user=request.user).count()
        theme.completed = theme.done_essays > 0
        if theme.completed:
            theme.last_essay = Essay.objects.filter(theme=theme, user=request.user).first().upload_date
            axes[theme.axis]['done_themes'] += 1
            if theme.jury == 'ENEM':
               axes_enem[theme.axis]['done_themes'] += 1
            elif theme.jury == 'VUNESP':
               axes_vunesp[theme.axis]['done_themes'] += 1
            elif theme.jury == 'CESPE':
               axes_cespe[theme.axis]['done_themes'] += 1
        themes.append(theme)
    
    axes_l = []
    for axis in sorted(axes.keys(), key=lambda axis: axis if axis != 'Outros eixos' else 'zzzzzzzzzzzzzzzzzzzz'):
        axes_l.append(axes[axis])
        
    axes_enem_l = []
    for axis in sorted(axes_enem.keys(), key=lambda axis: axis if axis != 'Outros eixos' else 'zzzzzzzzzzzzzzzzzzzz'):
        axes_enem_l.append(axes_enem[axis])
        
    axes_vunesp_l = []
    for axis in sorted(axes_vunesp.keys(), key=lambda axis: axis if axis != 'Outros eixos' else 'zzzzzzzzzzzzzzzzzzzz'):
        axes_vunesp_l.append(axes_vunesp[axis])
        
    axes_cespe_l = []
    for axis in sorted(axes_cespe.keys(), key=lambda axis: axis if axis != 'Outros eixos' else 'zzzzzzzzzzzzzzzzzzzz'):
        axes_cespe_l.append(axes_cespe[axis])

    data = {
        'title': 'Temas',
        'axes': axes_l,
        'axes_enem': axes_enem_l,
        'axes_vunesp': axes_vunesp_l,
        'axes_cespe': axes_cespe_l,
        'themes': themes,
        'user': get_user_details(request.user),
    }
    return render(request, 'themes.html', data)


@login_required
def theme_view(request, id):
    theme = Theme.objects.filter(id=id).first()
    data = {
        'title': 'Temas',
        'theme': theme,
        'user': get_user_details(request.user),
    }
    return render(request, 'theme.html', data)
