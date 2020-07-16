from django.shortcuts import render
from django.utils.timezone import now
from essay_manager.decorators import login_required
from essay_manager.models import Theme, Essay
from essay_manager.utils import get_user_details

@login_required
def themes_view(request):
    themes = list(Theme.objects.filter(start_date__lt=now(), end_date__gt=now()))
    for theme in themes:
        theme.completed = len(list(Essay.objects.filter(theme=theme, user=request.user).all())) > 0
    
    data = {
        'title': 'Temas',
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
