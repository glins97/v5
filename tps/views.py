from django.shortcuts import render
from tps.models import TPS, TPSAnswer, Question
from django.utils.timezone import now

def tps_view(request, id, campus, subject, week):
    tpses = TPS.objects.filter(id=id)
    if tpses.count():
        tps = tpses.get()
        answers = TPSAnswer.objects.all().filter(tps=tps)
        if len(answers) >= tps.max_answers:
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Número limite de respostas já atingido.'})
        if tps.start_date > now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Respostas serão liberadas apenas no dia {}.'.format(tps.start_date.strftime("%d/%m/%Y às %H:%M:%S"))})
        if tps.end_date < now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Tempo limite de resposta excedido.'})

        data = {
            'id': id,
            'subject': subject,
            'subject_desc': {
                'QUI': 'Química',
                'BIO': 'Biologia',
                'MAT': 'Matemática',
                'FIS': 'Física',
            }.get(subject.upper(), subject.capitalize()),
            'campus': campus,
            'week': week,
            'questions': Question.objects.filter(tps=tps),
        }
        return render(request, 'tps.html', data)
    return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Nenhum tps foi encontrado. Entre em contato com o responsável.'})
