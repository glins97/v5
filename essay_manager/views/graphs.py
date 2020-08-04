from django.shortcuts import render
from essay_manager.decorators import has_permission
from essay_manager.models import Essay, Correction
from essay_manager.utils import get_user_details
import json

@has_permission('student')
def graphs_view(request):
    essays = Essay.objects.filter(user=request.user).order_by('-id')

    grades = []
    gradesc1 = []
    gradesc2 = []
    gradesc3 = []
    gradesc4 = []
    gradesc5 = []
    for essay in essays:
        has_correction = False
        for correction in Correction.objects.filter(essay=essay):
            if correction.status == 'DONE':
                grades.append(essay.grade)
                comp = json.loads(correction.data)['competencies']['grades']
                gradesc1.append(int(comp['a1']))
                gradesc2.append(int(comp['a2']))
                gradesc3.append(int(comp['a3']))
                gradesc4.append(int(comp['a4']))
                gradesc5.append(int(comp['a5']))

    data = {
        'title': 'Performance',
        'grades': str(grades[::-1]),
        'gradesc1': str(gradesc1[::-1]),
        'gradesc2': str(gradesc2[::-1]),
        'gradesc3': str(gradesc3[::-1]),
        'gradesc4': str(gradesc4[::-1]),
        'gradesc5': str(gradesc5[::-1]),
        'avg_gradesc1': '{:.0f}'.format(sum(gradesc1) / len(gradesc1)),
        'avg_gradesc2': '{:.0f}'.format(sum(gradesc2) / len(gradesc2)),
        'avg_gradesc3': '{:.0f}'.format(sum(gradesc3) / len(gradesc3)),
        'avg_gradesc4': '{:.0f}'.format(sum(gradesc4) / len(gradesc4)),
        'avg_gradesc5': '{:.0f}'.format(sum(gradesc5) / len(gradesc5)),
        'user': get_user_details(request.user), 
    }

    return render(request, 'graphs.html', data)
