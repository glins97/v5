from essay_manager.decorators import login_required
from django.shortcuts import redirect

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
    except:
        return redirect('/profile/?updated=False')