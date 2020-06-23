from django.shortcuts import render

def tps_view(request, subject, week):
    return render(request, 'tps.html', {'saved': request.GET.get('saved', False)})

