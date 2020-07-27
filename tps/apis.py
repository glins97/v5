from django.shortcuts import render
from tps.models import TPS, TPSAnswer, Question, QuestionAnswer
from django.utils.timezone import now

def save_tps_answer(request, id):
    tpses = TPS.objects.all().filter(id=id)
    if tpses.count():
        tps = tpses.get()
        answers = TPSAnswer.objects.all().filter(tps=tps)
        if answers.count() >= tps.max_answers:
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Número limite de respostas já atingido.'})
        if tps.start_date > now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Respostas serão liberadas apenas em {}.'.format(tps.start_date)})
        if tps.end_date < now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Tempo limite de resposta excedido.'})
        if not request.POST.get('name', False) or not request.POST.get('email', False):
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Favor preencher nome e email!'})
        if TPSAnswer.objects.all().filter(tps=tps, name=request.POST.get('name', '')).count() or TPSAnswer.objects.all().filter(tps=tps, email=request.POST.get('email', '')).count():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Apenas uma resposta por aluno.'})

        tps_answer = TPSAnswer(
            tps=tps,
            name = request.POST.get('name', ''),
            email = request.POST.get('email', ''),
        )
        tps_answer.save()
        for attr in request.POST:
            if attr[0] == 'q':
                number = int(attr[1:])
                question = Question.objects.get(tps=tps, number=number)
                QuestionAnswer(question=question, tps_answer=tps_answer, answer=request.POST[attr]).save()
                if request.POST[attr][0] == question.correct_answer:
                    tps_answer.grade += 1
        
        tps_answer.save()
        return render(request, 'feed.html', {'title': 'Salvo!', 'description': 'O trabalho duro vence o talento.'})
    return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Nenhum tps foi encontrado. Entre em contato com o responsável.'})

