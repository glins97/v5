from django.shortcuts import render
from essay_manager.decorators import has_permission
from essay_manager.models import Essay, Correction
from essay_manager.utils import get_user_details
import json

def get_user_grades_enem(user):
    essays = Essay.objects.filter(user=user, theme__jury='ENEM').order_by('-id')

    grades = []
    gradesc1 = []
    gradesc2 = []
    gradesc3 = []
    gradesc4 = []
    gradesc5 = []
    for essay in essays:
        if essay.has_correction():
            grades.append(essay.grade)
            comp = json.loads(Correction.objects.get(essay=essay).data)['competencies']['grades']
            gradesc1.append(int(comp['a1']))
            gradesc2.append(int(comp['a2']))
            gradesc3.append(int(comp['a3']))
            gradesc4.append(int(comp['a4']))
            gradesc5.append(int(comp['a5']))

    return {
        'title': 'Performance',
        'grades': str(grades[::-1]),
        'gradesc1': str(gradesc1[::-1]),
        'gradesc2': str(gradesc2[::-1]),
        'gradesc3': str(gradesc3[::-1]),
        'gradesc4': str(gradesc4[::-1]),
        'gradesc5': str(gradesc5[::-1]),
        'avg_gradesc1': '{:.0f}'.format((sum(gradesc1) / len(gradesc1)) if gradesc1 else 0),
        'avg_gradesc2': '{:.0f}'.format((sum(gradesc2) / len(gradesc2)) if gradesc2 else 0),
        'avg_gradesc3': '{:.0f}'.format((sum(gradesc3) / len(gradesc3)) if gradesc3 else 0),
        'avg_gradesc4': '{:.0f}'.format((sum(gradesc4) / len(gradesc4)) if gradesc4 else 0),
        'avg_gradesc5': '{:.0f}'.format((sum(gradesc5) / len(gradesc5)) if gradesc5 else 0),
    }


@has_permission('student')
def graphs_view(request):
    data = {
        'title': 'Performance',
        'user': get_user_details(request.user), 
    }

    return render(request, 'graphs.html', { **data, **get_user_grades_enem(request.user) })
