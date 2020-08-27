from django.shortcuts import render
from django.contrib.auth.models import User
from essay_manager.decorators import login_required, has_permission
from essay_manager.utils import get_user_details
from essay_manager.models import Mentoring, Essay

@has_permission('superuser')
def mentoring_view(request):
    students = sorted(
        [user for user in User.objects.all() if user.groups.filter(name='student').exists()],
        key=lambda student: student.first_name + student.last_name
    )
    for student in students:
        mentoring = Mentoring.objects.filter(student=student, active=True).first()
        if mentoring:
            student.mentoring = mentoring
        student.last_essay = Essay.objects.filter(user=student).last()
        if not student.last_essay:
            student.last_essay = '-'

    
    mentored_students = sorted(
        [user for user in User.objects.all() if user.groups.filter(name='student').exists() and Mentoring.objects.filter(student=user, mentor=request.user, active=True,).count()],
        key=lambda student: student.first_name + student.last_name
    )
    for student in mentored_students:
        mentoring = Mentoring.objects.filter(student=student, mentor=request.user, active=True,).first()
        if mentoring:
            student.mentoring = mentoring
        student.last_essay = Essay.objects.filter(user=student).last()
        if not student.last_essay:
            student.last_essay = '-'
    data = {
        'title': 'Mentoria',
        'user': get_user_details(request.user),
        'students': students,
        'mentored_students': mentored_students,
    }
    return render(request, 'mentoring.html', data)
