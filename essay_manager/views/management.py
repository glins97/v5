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

def append_results(user, value):
    return (value if value != '-' else 0)  + {
        'felipemartins': 80,
        'riemma': 75,
        'naragomes': 58,
        'belaelaine': 40,
        'nadiasuelen': 34,
        'iasmincruz': 8,
    }.get(user.username, 0)

def get_corrections_data(user, start_date, end_date):

    class CorrectionData():
        def __init__(self, **kwargs):
            for kw in kwargs:
                setattr(self, kw, kwargs[kw])

    corrections = Correction.objects.filter(start_date__gte=start_date, end_date__lte=end_date, user=user, status='DONE')
    data = CorrectionData(
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
    print(user, [correction.essay.theme.description for correction in corrections])
    data.free_corrections = len([correction for correction in corrections if correction.essay.theme.description=='Solidário'])
    data.paid_corrections = len([correction for correction in corrections if correction.essay.theme.description!='Solidário'])
    return data

@has_permission('superuser')
def management_view(request):
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
        # # calculations -----------
        # # ------------------------
        # monitor_done_corrections = Correction.objects.filter(user=monitor, status='DONE')
        # monitor_average_grade = avg([
        #     correction.essay.grade for correction in monitor_done_corrections
        # ])

        # monitor_total_correction_time = 0
        # monitor_done_corrections_count = 0
        # monitor_valid_corrections_count = 0
        # monitor_average_correction_time = 0
        # for correction in monitor_done_corrections:
        #     total_corrections += 1
        #     monitor_done_corrections_count += 1
        #     total_grade += correction.essay.grade
        #     td = min(abs((correction.end_date - correction.start_date).seconds), abs((correction.start_date - correction.end_date).seconds)) / 60
        #     if td >= 2 and td < 120: # min is 2 minutes, max is 2 hours, else something mustve went wrong
        #         total_correction_time += td 
        #         monitor_valid_corrections_count += 1
        #         total_valid_corrections += 1
        #         monitor_total_correction_time += td
        
        # if monitor_valid_corrections_count > 0:
        #     monitor_average_correction_time = monitor_total_correction_time / monitor_valid_corrections_count
        # # ------------------------

        # # legibility changes -----
        # # ------------------------
        # if numpy.isnan(monitor_average_grade):
        #     monitor_average_grade = '-'
        # else:
        #     monitor_average_grade = '{:.0f}'.format(monitor_average_grade)

        # if monitor_done_corrections_count == 0:
        #     monitor_done_corrections_count = '-'

        # if monitor_average_correction_time == 0:
        #     monitor_average_correction_time = '-'
        
        # if monitor_total_correction_time == 0:
        #     monitor_total_correction_time = '-'
        # # ------------------------

        # monitor.monitor_average_grade = monitor_average_grade
        # monitor.monitor_done_corrections_count = append_results(monitor, monitor_done_corrections_count)
        # monitor.monitor_average_correction_time = minute_format(monitor_average_correction_time)
        # monitor.monitor_total_correction_time = hour_format(monitor_total_correction_time)

        # week_corrections = Correction.objects.filter(user=monitor, start_date__gte=now() - timedelta(days=7), status='DONE')
        # monitor.week_avg_grade = avg([correction.essay.grade for correction in week_corrections])
        # monitor.week_avg_grade = int(monitor.week_avg_grade) if monitor.week_avg_grade == monitor.week_avg_grade else '-' # nan check
        # monitor.week_paid_corrections = sum([1 for correction in week_corrections if correction.essay.theme.description!='Solidário'])
        # monitor.week_free_corrections = sum([1 for correction in week_corrections if correction.essay.theme.description=='Solidário'])

        # month_corrections = Correction.objects.filter(user=monitor, start_date__gte=now() - timedelta(days=31), status='DONE')
        # monitor.month_avg_grade = avg([correction.essay.grade for correction in month_corrections])
        # monitor.month_avg_grade = int(monitor.month_avg_grade) if monitor.month_avg_grade == monitor.month_avg_grade else '-' # nan check
        # monitor.month_paid_corrections = sum([1 for correction in month_corrections if correction.essay.theme.description!='Solidário'])
        # monitor.month_free_corrections = sum([1 for correction in month_corrections if correction.essay.theme.description=='Solidário'])
    
    print([monitor.alltime_data.average_correction_time for monitor in monitors if monitor.alltime_data.total_corrections > 0])
    data = {
        'title': 'Gestão',
        'user': get_user_details(request.user),
        'monitors': [monitor for monitor in monitors if monitor.alltime_data.total_corrections > 0],
        'average_grade': '{:.0f}'.format(avg([monitor.alltime_data.average_grade for monitor in monitors if monitor.alltime_data.total_corrections > 0 and monitor.alltime_data.average_grade == monitor.alltime_data.average_grade])),
        'average_correction_time': minute_format(avg([monitor.alltime_data.average_correction_time for monitor in monitors if monitor.alltime_data.total_corrections > 0 and monitor.alltime_data.average_correction_time == monitor.alltime_data.average_correction_time])), 
    }
    return render(request, 'management.html', data)
