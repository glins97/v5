from essay_manager.models import Profile
from essay_manager.decorators import login_required, has_permission
from django.contrib.auth.models import Group
from django.shortcuts import redirect
import logging
logger = logging.getLogger()

@login_required
def update_profile_endpoint(request):
    try:
        profile = Profile.objects.get(user=request.user)
        for attr in request.POST:
            setattr(profile, attr, request.POST[attr])
        profile.save()

        updated_user = False
        if 'user__first_name' in request.POST:
            updated_user = True
            request.user.first_name = request.POST['user__first_name']
        if 'user__last_name' in request.POST:
            updated_user = True
            request.user.last_name = request.POST['user__last_name']
        
        if updated_user:
            request.user.save()
        return redirect('/profile/?updated=True')
    except Exception as e:
        logger.error(f'Error updating profile. Error {e}', exc_info=e)
        return redirect('/profile/?updated=False')

@has_permission('superuser')
def update_al_profile_endpoint(request, level):
    try:
        for level_ in ['student', 'monitor']:
            request.user.groups.remove(Group.objects.get(name=level_))
        request.user.groups.add(Group.objects.get(name=level))
        request.user.save()
        return redirect('/')
    except Exception as e:
        logger.error(f'Error updating profile al. Error {e}', exc_info=e)
        return redirect('/')