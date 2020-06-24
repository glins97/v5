from django.contrib.auth import authenticate
from django.contrib.auth import login as login_
from django.shortcuts import redirect

def login_endpoint(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    authed = False
    if user is not None:
        authed = True
        login_(request, user)
    return redirect(f'/?authed={authed}')