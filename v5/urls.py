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
from essay_manager.utils import get_uploaded_file

from bauth.views import *
from bauth.apis import *

from tps.views import *
from tps.apis import *

def base_redirect(request):
    if request.user.groups.filter(name='tps').exists():
        return redirect('/admin/')
    return dashboard_view(request)

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

    # - apis
    path('mail/<int:id>/', mail_essay_endpoint),
    path('corrections/new/<int:id>/', create_correction_endpoint),
    path('corrections/update/<int:id>/', update_correction_endpoint),
    path('api/profile/update/', update_profile_endpoint),
    path('api/essays/create/', create_essay_endpoint),
    path('uploads/<str:url>/', get_uploaded_file),
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
    path('tps/<str:campus>/<str:subject>/<int:week>/', tps_view),

    # - apis
    path('tps/answer/<str:campus>/<str:subject>/<int:week>', save_tps_answer)
    # ---------------------
] 


handler404 = 'bauth.views.e404_view'
handler500 = 'bauth.views.e500_view'

admin.site.site_header = 'PPA Digital'
admin.site.site_title = 'PPA Digital'
admin.site.index_title = 'PPA Digital'