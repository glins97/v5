from django.contrib.auth import authenticate
from django.contrib.auth import login as login_
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_endpoint(request):
    username = request.POST['username']
    password = request.POST['password']
    for username_ in [username, username.lower()]:
        user = authenticate(request, username=username_, password=password)
        authed = False
        if user is not None:
            authed = True
            login_(request, user)
    return redirect(f'/?authed={authed}')