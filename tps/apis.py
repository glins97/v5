from django.shortcuts import render
from tps.models import TPS, TPSAnswer, Question, QuestionAnswer
from django.utils.timezone import now
from django.http import JsonResponse

def get_or_create(class_, *args, **kwargs):
    obj = class_.objects.filter(*args, **kwargs).first()
    if not obj:
        obj = class_(*args, **kwargs)
        obj.save()
    return obj

def save_tps_answer(request, id):
    tpses = TPS.objects.filter(id=id)
    if tpses.count():
        tps = tpses.get()
        answers = TPSAnswer.objects.filter(tps=tps)
        if answers.count() >= tps.max_answers:
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Número limite de respostas já atingido.'})
        if tps.start_date > now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Respostas serão liberadas apenas em {}.'.format(tps.start_date)})
        if tps.end_date < now():
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Tempo limite de resposta excedido.'})
        if not request.POST.get('name', False) or not request.POST.get('email', False):
            return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Favor preencher nome e email!'})
      
        tps_answer = get_or_create(TPSAnswer,
            tps=tps,
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
        )
        tps_answer.grade = 0
        tps_answer.save()
        for attr in request.POST:
            if attr[0] == 'q':
                number = int(attr[1:])
                question = Question.objects.get(tps=tps, number=number)
                question_answer = get_or_create(QuestionAnswer, question=question, tps_answer=tps_answer)
                question_answer.answer = request.POST[attr]
                question_answer.save()
                if request.POST[attr][0] == question.correct_answer:
                    tps_answer.grade += 1
        
        tps_answer.save()
        return render(request, 'feed.html', {'title': 'Salvo!', 'description': 'O trabalho duro vence o talento.'})
    return render(request, 'feed.html', {'title': 'Opa!', 'description': 'Nenhum tps foi encontrado. Entre em contato com o responsável.'})

def get_tps_delivery_date(request, id):
    try:
        tps = TPS.objects.get(id=id)
        return JsonResponse({
            'year': tps.end_date.year,
            'month': tps.end_date.month,
            'day': tps.end_date.day,
            'hour': tps.end_date.hour,
            'minute': tps.end_date.minute,
        }, safe=False)
    except:
        return JsonResponse({}, status=500, safe=False)
