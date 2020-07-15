from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
import logging
logger = logging.getLogger()

def register_endpoint(request):
    if request.POST['password'] != request.POST['password-confirmation']:
        return redirect(f'/register/?registered=False')
    try:
        user = User(
            username=request.POST['username'],
            password=request.POST['password'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'])
        user.save()

        group = Group.objects.get(name='student')
        user.groups.add(group)
        user.save()
        login(request, user)
        return redirect(f'/registered?True')
    except Exception as e:
        logger.error('Error registering user {}. Error {}'.format(request.POST['username'], e), exc_info=e)
        return redirect(f'/register/?registered=False')
