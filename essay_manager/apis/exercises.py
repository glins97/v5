from django.shortcuts import redirect
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import InterestedExerciseList, ExerciseList

import logging
logger = logging.getLogger('django')

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
        