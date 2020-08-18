from django.shortcuts import render
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Correction, Essay
from essay_manager.utils import get_user_details
from django.contrib.auth.models import User
from logging import getLogger
import numpy

logger = getLogger('django')
def hour_format(minutes):
    if minutes != '-':
        return '{:.0f}h'.format(minutes / 60)
    return minutes

def minute_format(minutes):
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

@has_permission('superuser')
def management_view(request):
    monitors = User.objects.filter(groups__name='monitor')
    total_grade = 0
    total_correction_time = 0
    total_corrections = 0
    total_valid_corrections = 0 # this only counts corrections that have a valid timedelta
    for monitor in monitors:

        # calculations -----------
        # ------------------------
        monitor_done_corrections = Correction.objects.filter(user=monitor, status='DONE')
        monitor_average_grade = numpy.mean([
            correction.essay.grade for correction in monitor_done_corrections
        ])

        monitor_total_correction_time = 0
        monitor_done_corrections_count = 0
        monitor_valid_corrections_count = 0
        monitor_average_correction_time = 0
        for correction in monitor_done_corrections:
            total_corrections += 1
            monitor_done_corrections_count += 1
            total_grade += correction.essay.grade
            td = min(abs((correction.end_date - correction.start_date).seconds), abs((correction.start_date - correction.end_date).seconds)) / 60
            if td >= 2 and td < 120: # min is 2 minutes, max is 2 hours, else something mustve went wrong
                total_correction_time += td 
                monitor_valid_corrections_count += 1
                total_valid_corrections += 1
                monitor_total_correction_time += td
        
        if monitor_valid_corrections_count > 0:
            monitor_average_correction_time = monitor_total_correction_time / monitor_valid_corrections_count
        # ------------------------

        # legibility changes -----
        # ------------------------
        if numpy.isnan(monitor_average_grade):
            monitor_average_grade = '-'
        else:
            monitor_average_grade = '{:.0f}'.format(monitor_average_grade)

        if monitor_done_corrections_count == 0:
            monitor_done_corrections_count = '-'

        if monitor_average_correction_time == 0:
            monitor_average_correction_time = '-'
        
        if monitor_total_correction_time == 0:
            monitor_total_correction_time = '-'
        # ------------------------

        monitor.monitor_average_grade = monitor_average_grade
        monitor.monitor_done_corrections_count = append_results(monitor, monitor_done_corrections_count)
        monitor.monitor_average_correction_time = minute_format(monitor_average_correction_time)
        monitor.monitor_total_correction_time = hour_format(monitor_total_correction_time)
        
    data = {
        'title': 'Gestão',
        'user': get_user_details(request.user),
        'monitors': [monitor for monitor in monitors if monitor.monitor_done_corrections_count > 0],
        'average_grade': '{:.0f}'.format(total_grade / total_corrections) if total_corrections else '-',
        'average_correction_time': minute_format(total_correction_time / total_valid_corrections) if total_valid_corrections else '-', 
    }
    return render(request, 'management.html', data)
