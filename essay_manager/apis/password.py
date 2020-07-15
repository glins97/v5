from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
from essay_manager.decorators import login_required
from django.shortcuts import redirect
import logging
logger = logging.getLogger()

@login_required
def change_password_endpoint(request):
    username = request.user.username
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    try:
        if user is not None:
            if request.POST['password-new'] == request.POST['password-new-confirmation']:
                user.set_password(request.POST['password-new'])
                user.save()
                update_session_auth_hash(request, user)
                return redirect('/profile/?updated=True')
            return redirect('/profile/?updated=False')
        return redirect('/profile/?updated=False')
    except Exception as e:
        logger.error(f'Error changing user {user} password. Error {e}', exc_info=e)
        return redirect('/profile/?updated=False')
