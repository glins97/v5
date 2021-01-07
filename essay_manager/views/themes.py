from django.shortcuts import render
from django.utils.timezone import now
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Theme, Essay
from essay_manager.utils import get_view_by_permission, get_user_details

def get_jury_data(jury=None, user=None):
    themes = Theme.objects.filter()
    if jury: themes = Theme.objects.filter(jury=jury)
    axes = themes.order_by().values('axis').distinct()
    return [item for item in [get_axis_data(axis['axis'], jury, user) for axis in axes] if item['themes']]

def get_axis_data(axis, jury=None, user=None):
    done = 0
    themes = Theme.objects.filter(active=True, axis=axis)
    if jury: themes = themes.filter(jury=jury)
    for theme in themes:
        essays = Essay.objects.filter(theme=theme)
        if user:
            essays = essays.filter(user=user) 
        theme.last_essay = '-'
        theme.essay_count = essays.count()
        if theme.essay_count:
            done += 1
            theme.last_essay = essays.last().upload_date
    return {
        'description': axis,
        'themes': themes,
        'total': themes.count(),
        'done': done,
    }

@has_permission('student')
@login_required
def _student_themes_view(request):
    themes_by_axes = {
        'all': get_jury_data(user=request.user),
        'enem': get_jury_data(jury='ENEM', user=request.user),
        'vunesp': get_jury_data(jury='VUNESP', user=request.user),
        'cespe': get_jury_data(jury='CESPE', user=request.user),
    }

    data = {
        'title': 'Temas',
        'themes_by_axes': themes_by_axes,
        'user': get_user_details(request.user),
    }
    return render(request, 'themes/student.html', data)


@has_permission('superuser')
@login_required
def _superuser_themes_view(request):
    themes_by_axes = {
        'all': get_jury_data(),
        'enem': get_jury_data(jury='ENEM'),
        'vunesp': get_jury_data(jury='VUNESP'),
        'cespe': get_jury_data(jury='CESPE'),
    }

    data = {
        'title': 'Temas',
        'themes_by_axes': themes_by_axes,
        'user': get_user_details(request.user),
    }
    return render(request, 'themes/superuser.html', data)

def themes_view(request):
    return get_view_by_permission(request, **{
        'student': _student_themes_view,
        'superuser': _superuser_themes_view,
    })

@login_required
def theme_view(request, id):
    theme = Theme.objects.filter(id=id).first()
    data = {
        'title': 'Temas',
        'theme': theme,
        'user': get_user_details(request.user),
    }
    return render(request, 'theme.html', data)
