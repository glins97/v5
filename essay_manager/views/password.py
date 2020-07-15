from django.shortcuts import render
from essay_manager.decorators import login_required
from essay_manager.models import Profile
from essay_manager.utils import get_user_details

@login_required
def change_password_view(request):
    data = {
        'title': 'Perfil',
        'updated': request.GET.get('updated', 'None'),
        'user': get_user_details(request.user),
    }
    return render(request, 'password.html', data)