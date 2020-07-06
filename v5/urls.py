"""v5 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from essay_manager.views import *
from essay_manager.apis import *
from essay_manager.utils import get_essay_file

from bauth.views import *
from bauth.apis import *

from tps.views import *
from tps.apis import *

import os.path
import mimetypes

def base_redirect(request):
    if request.user.groups.filter(name='tps').exists():
        return redirect('/admin/')
    return dashboard_view(request)

def uploaded_file_redirect(request, url):
    if 'uploads/' not in url:
        url = 'uploads/' + url

    # if file is from an essay, use essay manager's 
    # file serving function 'get_essay_file'
    if Essay.objects.filter(file=url):
        return get_essay_file(request, url)
    
    # else, serve file as usual
    mimetypes.init()
    try:
        fsock = open(url, "rb")
        file_name = os.path.basename(url) 
        mime_type_guess = mimetypes.guess_type(file_name)
        if mime_type_guess is not None:
            response = HttpResponse(fsock, content_type=mime_type_guess[0])
        response['Content-Disposition'] = 'attachment; filename=' + file_name            
    except IOError:
        response = e500_view(request)
    return response

urlpatterns = [    
    path('admin/', admin.site.urls),

    # ESSAY MANAGER RELATED
    # - views
    path('', base_redirect),
    path('essays/', essays_view),
    path('essays/<int:id>/', essay_view),
    path('essays/new/', create_essay_view),
    path('corrections/', corrections_view),
    path('profile/', profile_view),
    path('themes/', themes_view),
    path('management/', management_view),

    # - apis
    path('mail/<int:id>/', mail_essay_endpoint),
    path('corrections/new/<int:id>/', create_correction_endpoint),
    path('corrections/update/<int:id>/', update_correction_endpoint),
    path('api/profile/update/', update_profile_endpoint),
    path('api/essays/create/', create_essay_endpoint),
    path('uploads/<str:url>/', uploaded_file_redirect),
    # ---------------------

    # BAUTH RELATED
    # - views
    path('login/', login_view),

    # - apis
    path('api/logout/', logout_endpoint),
    path('api/login/', login_endpoint),
    # ---------------------

    # TPS RELATED
    # - views
    path('tps/<int:id>/<str:campus>/<str:subject>/<int:week>/', tps_view),

    # - apis
    path('tps/answer/<int:id>/', save_tps_answer)
    # ---------------------
] 

handler404 = 'bauth.views.e404_view'
handler500 = 'bauth.views.e500_view'

admin.site.site_header = 'PPA Digital'
admin.site.site_title = 'PPA Digital'
admin.site.index_title = 'PPA Digital'