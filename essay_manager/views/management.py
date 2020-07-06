from django.shortcuts import render
from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Correction, Essay
from essay_manager.utils import get_user_details
from django.contrib.auth.models import User

import numpy

def hour_format(minutes):
    if minutes != '-':
        return '{:.0f}h'.format(minutes / 60)
    return minutes

def minute_format(minutes):
    if minutes != '-':
        return '{:.0f}m'.format(minutes)
    return minutes

@has_permission('superuser')
def management_view(request):
    monitors = User.objects.filter(groups__name='monitor')
    total_grade = 0
    total_correction_time = 0
    total_corrections = 0
    for monitor in monitors:

        # calculations -----------
        # ------------------------
        monitor_done_corrections = Correction.objects.filter(user=monitor, status='DONE')
        monitor_average_grade = numpy.mean([
            correction.essay.grade for correction in monitor_done_corrections
        ])

        monitor_total_correction_time = 0
        monitor_done_corrections_count = 0
        monitor_average_correction_time = 0
        for correction in monitor_done_corrections:
            total_corrections += 1
            total_grade += correction.essay.grade
            td = (correction.end_date - correction.start_date)
            total_correction_time += td.seconds / 60
            if td.seconds > 60:
                monitor_total_correction_time += td.seconds / 60
                monitor_done_corrections_count += 1
        
        if monitor_done_corrections_count > 0:
            monitor_average_correction_time = monitor_total_correction_time / monitor_done_corrections_count
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
        monitor.monitor_done_corrections_count = monitor_done_corrections_count
        monitor.monitor_average_correction_time = minute_format(monitor_average_correction_time)
        monitor.monitor_total_correction_time = hour_format(monitor_total_correction_time)

    data = {
        'title': 'Gestão',
        'user': get_user_details(request.user),
        'monitors': monitors,
        'average_grade': '{:.0f}'.format(total_grade / total_corrections),
        'average_correction_time': minute_format(total_correction_time / total_corrections), 
    }
    return render(request, 'management.html', data)
