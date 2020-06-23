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

urlpatterns = [    
    path('admin/', admin.site.urls),

    # essay manager related
    # - views
    path('', dashboard_view),
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

    # login related
    # - views
    path('login/', login_view),

    # - apis
    path('api/logout/', logout_endpoint),
    path('api/login/', login_endpoint),
    # ---------------------

    # tps related
    path('tps/<str:subject>/<int:week>/', tps_view),
    # ---------------------
] 


handler404 = 'bauth.views.e404_view'
handler500 = 'bauth.views.e500_view'