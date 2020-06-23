from django.shortcuts import render
from django.utils.timezone import now
from essay_manager.decorators import login_required
from essay_manager.models import Theme
from essay_manager.utils import get_user_details

@login_required
def create_essay_view(request):
    data = {
        'title': 'Redações',
        'themes': [theme.description for theme in Theme.objects.filter(start_date__lt=now(), end_date__gt=now())],
        'added': request.GET.get('added', 'None'),
        'user': get_user_details(request.user),
    }
    return render(request, 'create_essay.html', data)