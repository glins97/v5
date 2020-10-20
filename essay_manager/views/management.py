from django.shortcuts import render
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Correction, Essay
from essay_manager.utils import get_user_details
from django.contrib.auth.models import User
from logging import getLogger
import numpy
from datetime import timedelta, datetime
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

logger = getLogger('django')
def avg(l):
    if not l: return 0
    s = 0
    for i in l:
        s += i
    return s / len(l)

def get_month_verbose(i):
    return {
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro',
    }.get(i, '-')

def hour_format(minutes):
    if minutes != minutes:
        return '-'
    if minutes != '-':
        return '{:.0f}h {:.0f}m'.format(minutes / 60, minutes - 60 * int(minutes / 60))
    return minutes

def minute_format(minutes):
    if minutes != minutes:
        return '-'
    if minutes != '-':
        return '{:.0f}m'.format(minutes)
    return minutes

class DataObject():
    def __init__(self, **kwargs):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

def get_student_data(start_date, end_date, student, jury):
    essays = Essay.objects.filter(upload_date__gte=start_date, upload_date__lte=end_date, user=student, theme__jury=jury).order_by('-id')
    for essay in essays:
        essay.get_correction_status()

    if essays:
        return DataObject(
            essays=essays,
            count=essays.count(),
            avgerage_grade=int(avg([essay.grade for essay in essays if essay.correction_status == 'DONE'])),
        )

def get_students_data(start_date, end_date, jury):
    students_essays = {
        student: [essay for essay in Essay.objects.filter(upload_date__gte=start_date, upload_date__lte=end_date, user=student, theme__jury=jury).exclude(theme__description='Solidário') if essay.has_correction()]
        for student in list(set([essay.user for essay in Essay.objects.filter(upload_date__gte=start_date, upload_date__lte=end_date, theme__jury=jury).exclude(theme__description='Solidário') if essay.has_correction()]))
    }

    student_data = []
    for student in students_essays:
        student_data.append(DataObject(
            student=student,
            count=len(students_essays[student]),
            average_grade=int(avg([essay.grade for essay in students_essays[student]]))
        ))
        
    return sorted(student_data, key=lambda obj: -obj.count)

def get_corrections_data(user, start_date, end_date):
    corrections = Correction.objects.filter(start_date__gte=start_date, end_date__lte=end_date, user=user, status='DONE')
    data = DataObject(
        start_date=start_date,
        end_date=end_date,
        average_grade=0,
        total_corrections=0,
        total_correction_time=0,
        average_correction_time=0,
        paid_corrections=0,
        free_corrections=0,
    )
    if not corrections.count():
        return data
    
    data.average_grade = int(avg([correction.essay.grade for correction in corrections]))
    data.total_corrections = corrections.count()
    data.total_correction_time = sum([(correction.end_date - correction.start_date).seconds / 60 for correction in corrections if (correction.end_date - correction.start_date).seconds < 3600])
    data.average_correction_time = avg([(correction.end_date - correction.start_date).seconds / 60 for correction in corrections if (correction.end_date - correction.start_date).seconds < 3600])
    data.total_correction_time_str = hour_format(data.total_correction_time)
    data.average_correction_time_str = minute_format(data.average_correction_time)
    data.free_corrections = len([correction for correction in corrections if correction.essay.theme.description=='Solidário'])
    data.paid_corrections = len([correction for correction in corrections if correction.essay.theme.description!='Solidário'])
    return data

@has_permission('superuser')
def management_monitors_view(request):
    monitors = User.objects.filter(groups__name='monitor')
    
    now_ = now()
    for monitor in monitors:
        monitor.alltime_data = get_corrections_data(monitor, now_ - timedelta(days=365 * 99), now_) 
        monitor.week_data = get_corrections_data(monitor, now_ - timedelta(days=7), now_) 
        monitor.month_data = get_corrections_data(monitor, now_ - timedelta(days=30), now_) 
        monitor.months = []

        base = datetime(year=2020, month=7, day=1)
        current_time = now()
        while current_time > base:
            month_base_datetime = datetime(year=current_time.year, month=current_time.month, day=1)
            month_data = get_corrections_data(monitor, month_base_datetime, month_base_datetime + relativedelta(months=1))
            month_data.month = get_month_verbose(current_time.month)
            monitor.months.append(month_data)
            current_time -= relativedelta(months=1)
            
    data = {
        'title': 'Gestão',
        'user': get_user_details(request.user),
        'monitors': [monitor for monitor in monitors if monitor.alltime_data.total_corrections > 0],
        'average_grade': '{:.0f}'.format(avg([monitor.alltime_data.average_grade for monitor in monitors if monitor.alltime_data.total_corrections > 0 and monitor.alltime_data.average_grade == monitor.alltime_data.average_grade])),
        'average_correction_time': minute_format(avg([monitor.alltime_data.average_correction_time for monitor in monitors if monitor.alltime_data.total_corrections > 0 and monitor.alltime_data.average_correction_time == monitor.alltime_data.average_correction_time])), 
    }
    return render(request, 'management/monitors.html', data)

@has_permission('superuser')
def management_students_view(request):
    now_ = now()

    data = {
        'title': 'Gestão',
        'user': get_user_details(request.user),
        'week_data_enem': get_students_data(now_ - relativedelta(days=7), now_, 'ENEM'),
        'biweek_data_enem': get_students_data(now_ - relativedelta(days=14), now_, 'ENEM'),
        'month_data_enem': get_students_data(now_ - relativedelta(days=30), now_, 'ENEM'),
        'all_data_enem': get_students_data(now_ - relativedelta(days=365 * 99), now_, 'ENEM'),
        
        'week_data_vunesp': get_students_data(now_ - relativedelta(days=7), now_, 'VUNESP'),
        'biweek_data_vunesp': get_students_data(now_ - relativedelta(days=14), now_, 'VUNESP'),
        'month_data_vunesp': get_students_data(now_ - relativedelta(days=30), now_, 'VUNESP'),
        'all_data_vunesp': get_students_data(now_ - relativedelta(days=365 * 99), now_, 'VUNESP'),
    }
    return render(request, 'management/students.html', data)

@has_permission('superuser')
def management_student_view(request, id):
    now_ = now()
    student = User.objects.get(id=id)
    data = {
        'title': 'Gestão',
        'user': get_user_details(request.user),
        'student': student,
        'enem_data': get_student_data(now_ - relativedelta(days=365 * 99), now_, student, 'ENEM'),
        'vunesp_data': get_student_data(now_ - relativedelta(days=365 * 99), now_, student, 'VUNESP'),
    }
    return render(request, 'management/student.html', data)
