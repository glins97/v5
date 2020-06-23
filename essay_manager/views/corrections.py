from django.shortcuts import render
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Essay, Correction
from essay_manager.utils import get_view_by_permission, get_user_details

@has_permission('monitor')
@login_required
def corrections_view(request):
    active_correction_essays = [essay for essay in Essay.objects.filter().order_by('id') if Correction.objects.filter(essay=essay, status='ACTIVE', user=request.user)]
    done_correction_essays = [essay for essay in Essay.objects.filter().order_by('-id') if Correction.objects.filter(essay=essay, status='DONE', user=request.user)]

    data = {
        'title': 'Correções',
        'active_correction_essays': active_correction_essays,
        'done_correction_essays': done_correction_essays[:10],
        'user': get_user_details(request.user),
    }
    return render(request, 'corrections.html', data)
