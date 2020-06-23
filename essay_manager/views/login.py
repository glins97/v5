from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html', {'authed': request.GET.get('authed', False)})
