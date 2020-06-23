from django.shortcuts import render

def e404_view(request, *args, **kwargs):
    return render(request, 'errors/e404.html')

def e403_view(request, *args, **kwargs):
    return render(request, 'errors/e403.html')

def e500_view(request, *args, **kwargs):
    return render(request, 'errors/e500.html')
