from django.contrib.auth import logout as logout_
from essay_manager.decorators import login_required
from django.shortcuts import redirect

@login_required
def logout_endpoint(request):
    logout_(request)
    return redirect('/login/')