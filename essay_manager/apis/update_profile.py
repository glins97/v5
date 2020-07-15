from essay_manager.models import Profile
from essay_manager.decorators import login_required
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

        request.user.first_name = request.POST['user__first_name']
        request.user.last_name = request.POST['user__last_name']
        request.user.save()
        return redirect('/profile/?updated=True')
    except Exception as e:
        logger.error(f'Error updating profile. Error {e}', exc_info=e)
        return redirect('/profile/?updated=False')