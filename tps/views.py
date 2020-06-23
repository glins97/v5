from django.shortcuts import render
from tps.models import TPS

def tps_view(request, campus, subject, week):
    tpses = list(TPS.objects.all().filter(campus=campus.upper(), subject=subject.upper(), week=week))
    if len(tpses):
        data = {
            'subject': subject,
            'subject_desc': {
                'QUI': 'Química',
                'BIO': 'Biologia',
                'MAT': 'Matemática',
                'FIS': 'Física',
            }[subject.upper()],
            'campus': campus,
            'week': week,
        }
        return render(request, 'tps.html', data)

def success_view(request):
    return render(request, 'success.html')

