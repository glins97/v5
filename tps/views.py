from django.shortcuts import render
from tps.models import TPS

def tps_view(request, campus, subject, week):
    tpses = list(TPS.objects.all().filter(campus=campus.upper(), subject=subject.upper(), week=week))
    if len(tpses):
        tps = tpses[0]
        answers = list(Answer.objects.all().filter(tps=tps))
        if len(answers) >= tps.max_answers:
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Número limite de respostas já atingido.'})

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
    return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Nenhum tps foi encontrado. Entre em contato com o responsável.'})
