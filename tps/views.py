from django.shortcuts import render
from tps.models import TPS, TPSAnswer, Question
from django.utils.timezone import now

def tps_view(request, id):
    tpses = TPS.objects.filter(id=id)
    if tpses.count():
        tps = tpses.get()
        answers = TPSAnswer.objects.all().filter(tps=tps)
        if len(answers) >= tps.max_answers:
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Número limite de respostas já atingido.'})
        
        if tps.questions:
            subject_desc = tps.subject
            supported_subjects = {
                'SIM': 'Simulado',
                'QUI': 'Química',
                'BIO': 'Biologia',
                'MAT': 'Matemática',
                'FIS': 'Física',
                'FIL': 'Filosofia',
            }
            for supported_subject in supported_subjects:
                if supported_subject in subject_desc.upper():
                    subject_desc = supported_subjects[supported_subject]
                    break            
            data = {
                'id': id,
                'subject_desc': subject_desc,
                'tps': tps,
                'now': now(),
                'questions': Question.objects.filter(tps=tps).order_by('number'),
            }
            return render(request, 'tps_questions.html', data)
        else:
            if tps.start_date > now():
                return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Respostas serão liberadas apenas no dia {}.'.format(tps.start_date.strftime("%d/%m/%Y às %H:%M:%S"))})
            if tps.end_date < now():
                return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Tempo limite de resposta excedido.'})

            data = {
                'id': id,
                'subject_desc': {
                    'QUI': 'Química',
                    'BIO': 'Biologia',
                    'MAT': 'Matemática',
                    'FIS': 'Física',
                    'FIL': 'Filosofia',
                    'SIM': 'Simulado',
                }.get(tps.subject.upper()[:3], tps.subject.title()),
                'tps': tps,
                'questions': Question.objects.filter(tps=tps).order_by('number'),
            }
            return render(request, 'tps.html', data)
            
    return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Nenhum tps foi encontrado. Entre em contato com o responsável.'})
