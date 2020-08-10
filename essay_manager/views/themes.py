from django.shortcuts import render
from django.utils.timezone import now
from essay_manager.decorators import login_required
from essay_manager.models import Theme, Essay
from essay_manager.utils import get_user_details

@login_required
def themes_view(request):
    themes = []
    axes = {}
    for theme in Theme.objects.filter(active=True):
        if theme.axis not in axes:
            axes[theme.axis] = {
                'description': theme.axis, 
                'total_themes': 1, 
                'done_themes': 0, 
            }
        else:
            axes[theme.axis]['total_themes'] += 1
        theme.completed = Essay.objects.filter(theme=theme, user=request.user).count() > 0
        if theme.completed:
            axes[theme.axis]['done_themes'] += 1
        themes.append(theme)
    
    axes_l = []
    for axis in sorted(axes.keys(), key=lambda axis: axis if axis != 'Outros eixos' else 'zzzzzzzzzzzzzzzzzzzz'):
        axes_l.append(axes[axis])

    data = {
        'title': 'Temas',
        'axes': axes_l,
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
