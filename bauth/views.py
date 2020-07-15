from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html', {'authed': request.GET.get('authed', False)})

def register_view(request):
    return render(request, 'register.html', {'registered': request.GET.get('registered', False)})

def register_confirmation_view(request):
    return render(request, 'register_confirmation.html')

def e404_view(request, *args, **kwargs):
    return render(request, 'errors/e404.html')

def e403_view(request, *args, **kwargs):
    return render(request, 'errors/e403.html')

def e500_view(request, *args, **kwargs):
    return render(request, 'errors/e500.html')
