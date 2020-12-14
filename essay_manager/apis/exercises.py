from django.shortcuts import redirect
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import InterestedExerciseList, ExerciseList, Essay
from django.http import JsonResponse, HttpResponse
import json
import logging
logger = logging.getLogger('django')

@has_permission('monitor')
def save_exercise_recommendation(request):
    response = HttpResponse()

    essay = int(request.POST.get('essay', '-1'))
    if essay == -1:
        response.status_code = 500
        return response

    essay = Essay.objects.get(id=essay)
    lists = json.loads(request.POST.get('lists', '[]'))
    for obj in InterestedExerciseList.objects.filter(essay=essay, user=essay.user):
        if obj.list.id not in lists:
            obj.delete()
        else:
            lists.remove(obj.list.id)

    for l in lists:
        InterestedExerciseList(essay=essay, list=ExerciseList.objects.get(id=l), user=essay.user).save()
    return response

@login_required
def interest_exercise_endpoint(request, id):
    try:
        list = InterestedExerciseList.objects.filter(user=request.user, list=ExerciseList.objects.get(id=id), completed=False).first()
        if not list:
            InterestedExerciseList(user=request.user, list=ExerciseList.objects.get(id=id)).save()
    except Exception as e:
        logger.error(f'interest_exercise_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
    return redirect('/exercises/')
        
@login_required
def uninterest_exercise_endpoint(request, id):
    try:
        list = InterestedExerciseList.objects.filter(user=request.user, list=ExerciseList.objects.get(id=id), completed=False).first()
        if list:
            list.delete()
    except Exception as e:
        logger.error(f'uninterest_exercise_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
    return redirect('/exercises/')
        

@login_required
def complete_exercise_endpoint(request, id):
    try:
        list = InterestedExerciseList.objects.filter(user=request.user, list=ExerciseList.objects.get(id=id), completed=False).first()
        if list:
            list.completed = True
            list.save()
        else:
            InterestedExerciseList(user=request.user, list=ExerciseList.objects.get(id=id), completed=True).save()
    except Exception as e:
        logger.error(f'complete_exercise_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
    return redirect('/exercises/')
        