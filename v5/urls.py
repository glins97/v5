from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
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

def manuals_file_redirect(request, manual, url):
    fn = f'uploads/manuals/{manual}/{url}'

    mimetypes.init()
    try:
        print('file_name', fn)
        fsock = open(fn, "rb")
        file_name = os.path.basename(fn) 
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
    path('themes/<int:id>/', theme_view),
    path('management/monitors/', management_monitors_view),
    path('management/students/', management_students_view),
    path('management/students/<int:id>/', management_student_view),
    path('mentoring/', mentoring_view),
    path('graphs/', graphs_view),
    path('exercises/<int:id>/', exercise_view),
    path('exercises/', exercises_view),
    path('password/change/', change_password_view),

    # - apis
    path('corrections/new/<int:id>/', create_correction_endpoint),
    path('corrections/update/<int:id>/', update_correction_endpoint),
    path('api/profile/update/', update_profile_endpoint),
    path('api/profile/access_level/<str:level>/', update_al_profile_endpoint),
    path('api/essays/mail/<int:id>/', mail_essay_endpoint),
    path('api/essays/download/<int:id>/', download_essay_endpoint),
    path('api/essays/create/', create_essay_endpoint),
    path('api/password/change/', change_password_endpoint),
    path('api/events/', get_events_endpoint),
    path('api/events/new/', create_event_endpoint),
    path('api/events/update/', update_event_endpoint),
    path('api/events/delete/', delete_event_endpoint),
    path('api/exercises/interest/<int:id>/', interest_exercise_endpoint),
    path('api/exercises/uninterest/<int:id>/', uninterest_exercise_endpoint),
    path('api/exercises/complete/<int:id>/', complete_exercise_endpoint),
    path('api/notifications/read/all/', read_all_notifications_endpoint),
    path('api/mentoring/start/<int:id>/', start_mentoring_endpoint),
    path('api/mentoring/finish/<int:id>/', finish_mentoring_endpoint),
    path('api/access_as/<int:id>/', access_as_endpoint),
    path('uploads/manuals/<str:manual>/<str:url>/', manuals_file_redirect),
    path('uploads/<str:url>/', uploaded_file_redirect),
    # ---------------------

    # BAUTH RELATED
    # - views
    path('login/', login_view),
    path('register/', register_view),
    path('register/confirmation/', register_confirmation_view),

    # - apis
    path('api/logout/', logout_endpoint),
    path('api/login/', login_endpoint),
    path('api/register/', register_endpoint),
    # ---------------------

    # TPS RELATED
    # - views
    re_path(r'tps/(?P<id>[\d-]+)/', tps_view, name='id'),
    re_path(r'tps/(?P<id>[\d-]+)/.+?/', tps_view, name='id'),
    re_path(r'tps/(?P<id>[\d-]+)/.+?/.+?/.+?/', tps_view, name='id'),

    # - apis
    path('tps/answer/<int:id>/', save_tps_answer),
    path('tps/delivery_date/<int:id>/', get_tps_delivery_date),
    # ---------------------
] 

handler404 = 'bauth.views.e404_view'
handler500 = 'bauth.views.e500_view'
handler400 = 'bauth.views.e500_view'

admin.site.site_header = 'PPA Digital'
admin.site.site_title = 'PPA Digital'
admin.site.index_title = 'PPA Digital'