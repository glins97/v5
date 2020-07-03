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
        if TPSAnswer.objects.all().filter(tps=tps, name=request.POST.get('name', '')).count():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Apenas uma resposta por aluno.'})
        if tps.start_date > now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Respostas serão liberadas apenas em {}.'.format(tps.start_date)})
        if tps.end_date < now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Tempo limite de resposta excedido.'})


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
        # answer = TPSAnswer(
        #     name = request.POST.get('name', ''),
        #     email = request.POST.get('email', ''),
        #     q1 = request.POST.get('q1', 'X'),
        #     q2 = request.POST.get('q2', 'X'),
        #     q3 = request.POST.get('q3', 'X'),
        #     q4 = request.POST.get('q4', 'X'),
        #     q5 = request.POST.get('q5', 'X'),
        #     q6 = request.POST.get('q6', 'X'),
        #     q7 = request.POST.get('q7', 'X'),
        #     q8 = request.POST.get('q8', 'X'),
        #     q9 = request.POST.get('q9', 'X'),
        #     q10 = request.POST.get('q10', 'X'),
        #     tps=tps,
        # )
        # for q in range(1, 11):
        #     if getattr(tps, 'q'+str(q)) == getattr(answer, 'q'+str(q)):
        #         answer.grade += 1
        # answer.save()
        return render(request, 'feed.html', {'title': 'Salvo!', 'description': 'O trabalho duro vence o talento.'})
    return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Nenhum tps foi encontrado. Entre em contato com o responsável.'})

