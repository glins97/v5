from django.shortcuts import redirect
from django.http import FileResponse
from django.utils.timezone import now

from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Theme, Essay, Correction
from essay_manager.apis.document import Document
from essay_manager.apis.pdf_filler import fill_pdf_fields
from mailer.mailer import send_mail
from v5.urls import api

import time
import subprocess
import json
import logging
logger = logging.getLogger('django')

@login_required
def create_essay_endpoint(request):
    try:
        obj = request.FILES['file'] 
        fn = 'uploads/{}_{}'.format(time.time(), str(obj).split('/')[-1].replace(' ', '_'))
        with open(fn, 'wb') as f:
            f.write(obj.file.read())
        
        id = request.POST['theme_id']
        if id == '-1':
            obj_theme = request.FILES['theme_file'] 
            fn_theme = 'uploads/THEME_{}_{}'.format(time.time(), str(obj_theme).split('/')[-1].replace(' ', '_'))
            with open(fn_theme, 'wb') as f:
                f.write(obj_theme.file.read())
            theme = Theme(
                description=request.POST['theme_name'], 
                jury=request.POST['theme_jury'],
                axis='De outros alunos',
                file=fn_theme,
                type='PAID',
            )
            theme.save()
        else:
            theme = Theme.objects.get(id=request.POST['theme_id'])

        Essay(user=request.user, theme=theme, file=fn, mode=request.POST['mode']).save()
        return redirect('/essays/?added=True')
    except Exception as e:
        logger.error(f'create_essay_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return redirect('/essays/?added=False')
        
def create_correction_pdf(request, id):
    final_destination = ''
    try:
        essay = Essay.objects.get(id=id)
        correction = Correction.objects.get(essay__id=id)
        doc = Document(str(essay.file))

        # export correction
        correction_destination = 'essay_manager/apis/exports/CORRECTION-{}-{}.pdf'.format(essay.id, correction.id)
        graded_destination = 'essay_manager/apis/exports/GRADED-{}-{}.pdf'.format(essay.id, correction.id)
        final_destination = 'static/essay_manager/pdf/FINAL-{}-{}.pdf'.format(essay.id, correction.id)
        data = json.loads(correction.data)
        
        # load grades, calculates total
        grades = data['competencies']['grades']
        grades['t'] = int(grades['a1']) + int(grades['a2']) + int(grades['a3']) + int(grades['a4']) + int(grades['a5'])

        # exports correction
        doc.export(correction_destination, data['objects'])
        
        # join with graded model
        subprocess.call(['/usr/bin/pdftk', correction_destination, 'essay_manager/apis/exports/model.PDF', 'cat',  'output', graded_destination], stdout=subprocess.PIPE)
        
        # fill joined pdf with data
        fill_pdf_fields(graded_destination, dict(grades, **data['competencies']['comments']) , final_destination)

    except Exception as e:
        print('exception', e)
        logger.error(f'create_correction_pdf@essay::Exception thrown | {request.user} {request} {repr(e)}')

    return final_destination

@has_permission('monitor')
@login_required
def download_essay_endpoint(request, id):
    essay = Essay.objects.get(id=id)
    final_destination = create_correction_pdf(request, id)
    return FileResponse(open(final_destination, 'rb'), as_attachment=True, filename=('CORRECAO-{}.pdf'.format(essay.user.first_name.upper())))

@has_permission('monitor')
@login_required
def mail_essay_endpoint(request, id):
    try:
        essay = Essay.objects.get(id=id)
        final_destination = create_correction_pdf(request, id)
        if not final_destination:
            return redirect('/essays/?mailed=False')

        mail_body = '<p>Sua redação corrigida se encontra em anexo! (ou, caso não, clique <a href="{}"> aqui</a>)<br>Para uma boa visualização, recomendamos abrir o arquivo com o Adobe Reader em um computador.</p>'.format('http://ppa.digital/{}'.format(final_destination))
        if send_mail(str(essay.user.username), 'redação corrigida!', mail_body, final_destination):
            essay.mailed = True
            essay.save()
            return redirect('/essays/?mailed=True')
        else:
            return redirect('/essays/?mailed=False')
    except Exception as e:
        logger.error(f'mail_essay_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return redirect('/essays/?mailed=False')

def get_correction_record_data(record):
    return [
        record.essay.id, 
        f'{record.essay.user}', 
        f'{record.user}', 
        f'{record.essay.theme.jury}', 
        f'{record.essay.theme.description.capitalize()}', 
        f'{record.essay.upload_date.strftime("%d de %B, %Y").title().replace("De", "de")}', 
        f'{record.essay.grade}', 
    ]
    
@api.post("tables/corrections/{status}/")
def get_table_data(request, status: str):
    response = {}
    try:
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 0))
        search = request.POST.get('search[value]', '')
    
        print('status', status)
        records = Correction.objects.filter(status=status.upper()).order_by('-id')
        records_filtered = []
    
        response['draw'] = draw
        response['recordsTotal'] = records.count()
        if search:
            filtered_record_data = []
            for record in records:
                record_data = get_correction_record_data(record)
                for attr in record_data:
                    if search.lower() in str(attr).lower():
                        filtered_record_data.append(record_data)
                        break
            response['recordsFiltered'] = len(filtered_record_data)
            response['data'] = [record_data for record_data in filtered_record_data[start : start + length]]
        else:
            records_filtered = list(records)
            response['recordsFiltered'] = len(records_filtered)
            response['data'] = [get_correction_record_data(record) for record in records[start : start + length]]

    except Exception as e:
        print('exception', e)
        response['error'] = e
    return response

def get_essay_record_data(record):
    return [
        record.id, 
        f'{record.user}', 
        f'Jornada {record.mode}', 
        f'{record.theme.jury}', 
        f'{record.theme.description.capitalize()}', 
        f'{record.upload_date.strftime("%d de %B, %Y").title().replace("De", "de")}', 
    ]

@api.post("tables/essays/{mode}/")
def get_table_data(request, mode: str):
    response = {}
    try:
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 0))
        search = request.POST.get('search[value]', '')
    
        records = Essay.objects.filter(correction__isnull=True, theme__type=mode.upper()) 
        records_filtered = []
        response['draw'] = draw
        response['recordsTotal'] = records.count()
        if search:
            filtered_record_data = []
            for record in records:
                record_data = get_essay_record_data(record)
                for attr in record_data:
                    if search.lower() in str(attr).lower():
                        filtered_record_data.append(record_data)
                        break
            response['recordsFiltered'] = len(filtered_record_data)
            response['data'] = [record_data for record_data in filtered_record_data[start : start + length]]
        else:
            records_filtered = list(records)
            response['recordsFiltered'] = len(records_filtered)
            response['data'] = [get_essay_record_data(record) for record in records[start : start + length]]

    except Exception as e:
        print('exception', e)
        response['error'] = e
    return response