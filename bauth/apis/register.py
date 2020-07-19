from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
import logging
logger = logging.getLogger()

def register_endpoint(request):
    if request.POST.get('password', '') != request.POST.get('password-confirmation', ''):
        return redirect(f'/register/?registered=False')
    try:
        print(request.POST)
        user = User.objects.create_user(
            username=request.POST.get('username', ''),
            password=request.POST.get('password', ''),
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''))
        user.save()

        group = Group.objects.get(name='student')
        user.groups.add(group)
        user.save()
        login(request, user)
        return redirect(f'/?registered=True')
    except Exception as e:
        logger.error('Error registering user {}. Error {}'.format(request.POST.get('username', ''), e), exc_info=e)
        return redirect(f'/register/?registered=False')
