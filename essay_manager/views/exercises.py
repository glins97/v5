from django.shortcuts import render
from essay_manager.decorators import has_permission
from essay_manager.utils import get_user_details
from essay_manager.models import ExerciseList, InterestedExerciseList

@has_permission('student')
def exercises_view(request):
    exercises = ExerciseList.objects.all()
    for exercise in exercises:
        last_completion =   InterestedExerciseList.objects.filter(user=request.user, completed=True, list=exercise).last()
        exercise.completion_count = InterestedExerciseList.objects.filter(user=request.user, completed=True, list=exercise).count()
        exercise.last_completion = '-'
        if last_completion:
            exercise.last_completion = last_completion.completion_date

    interests = InterestedExerciseList.objects.filter(user=request.user, completed=False)
    data = {
        'title': 'Exercícios',
        'exercises': exercises,
        'interests': interests,
        'user': get_user_details(request.user), 
    }

    return render(request, 'exercises.html', data)

@has_permission('student')
def exercise_view(request, id):
    data = {
        'title': 'Exercícios',
        'exercise': ExerciseList.objects.get(id=id),
        'user': get_user_details(request.user), 
    }

    return render(request, 'exercise.html', data)
