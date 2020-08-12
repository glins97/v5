from django.shortcuts import render
from essay_manager.decorators import login_required
from essay_manager.models import Profile
from essay_manager.utils import get_user_details

@login_required
def profile_view(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        profile = Profile(user=request.user, email=request.user.username)
        profile.save()

    data = {
        'title': 'Perfil',
        'updated': request.GET.get('updated', 'None'),
        'profile': {
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'zipcode': profile.zipcode,
            'course': profile.course,
            'faculty': profile.faculty,
            'school': profile.school,
            'email': profile.email,
            'target_grade': profile.target_grade,
            'target_production': profile.target_production,
            'phone': profile.phone,
            'not_specified': '-',
        },
        'user': get_user_details(request.user),
    }
    return render(request, 'profile.html', data)