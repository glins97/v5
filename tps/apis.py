from django.shortcuts import render
from tps.models import TPS, Answer
from django.utils.timezone import now

def save_tps_answer(request, campus, subject, week):
    tpses = list(TPS.objects.all().filter(campus=campus.upper(), subject=subject.upper(), week=week))
    if len(tpses):
        tps = tpses[0]
        answers = list(Answer.objects.all().filter(tps=tps))
        if len(answers) >= tps.max_answers:
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Número limite de respostas já atingido.'})
        if len(list(Answer.objects.all().filter(tps=tps, name=request.POST.get('name', '')))):
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Apenas uma resposta por aluno.'})
        if tps.start_date > now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Respostas serão liberadas apenas em {}.'.format(tps.start_date)})
        if tps.end_date < now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Tempo limite de resposta excedido.'})

        print(request.POST)
        answer = Answer(
            name = request.POST.get('name', ''),
            q1 = request.POST.get('q1', 'X'),
            q2 = request.POST.get('q2', 'X'),
            q3 = request.POST.get('q3', 'X'),
            q4 = request.POST.get('q4', 'X'),
            q5 = request.POST.get('q5', 'X'),
            q6 = request.POST.get('q6', 'X'),
            q7 = request.POST.get('q7', 'X'),
            q8 = request.POST.get('q8', 'X'),
            q9 = request.POST.get('q9', 'X'),
            q10 = request.POST.get('q10', 'X'),
            tps=tps,
        )
        for q in range(1, 11):
            if getattr(tps, 'q'+str(q)) == getattr(answer, 'q'+str(q)):
                answer.grade += 1
        answer.save()
        return render(request, 'feed.html', {'title': 'Salvo!', 'description': 'O trabalho duro vence o talento.'})
    return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Nenhum tps foi encontrado. Entre em contato com o responsável.'})

