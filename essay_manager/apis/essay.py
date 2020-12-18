from django.shortcuts import redirect
from django.http import FileResponse
from django.utils.timezone import now

from essay_manager.decorators import login_required, has_permission
from essay_manager.models import Theme, Essay, Correction
from essay_manager.apis.document import Document
from essay_manager.apis.pdf_filler import fill_pdf_fields
from mailer.mailer import send_templated_mail

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

@has_permission('monitor')
@login_required
def report_essay_endpoint(request, id):
    try:
        essay = Essay.objects.get(id=id)
        essay.reported = True
        essay.save()
        send_templated_mail('base.html', 'gabriel.lins97@gmail.com', 'Erro reportado', title=f'Redação #{id}', body=f'Erro reportado na redação #{id} pelo corretor {request.user}.<br>Favor averiguar.', footer="Equipe PPA")
    except Exception as e:
        logger.error(f'report_essay_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return redirect('/essays/?reported=False')
    return redirect('/essays/?reported=True')
        
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

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
import codecs
from threading import _start_new_thread
import logging
logger = logging.getLogger('django')

def send_mail(email, subject, message, attachment):
    try:
        msg = MIMEMultipart()
        password = 'campusppa'
        msg['To'] = email
        msg['From'] = 'PPA <contato@ppa.digital>'
        msg['Subject'] = subject

        if attachment:
            openedfile = None
            with open(attachment, 'rb') as opened:
                openedfile = opened.read()
            attachedfile = MIMEApplication(openedfile, _subtype = "pdf", _encoder=encode_base64)
            attachedfile.add_header('content-disposition', 'attachment', filename=attachment.split('/')[-1])
            msg.attach(attachedfile)
        msg.attach(MIMEText(message, 'html'))
        with smtplib.SMTP('smtp.gmail.com: 587') as server:
            server.starttls()
            server.login('adm.ppa.digital@gmail.com', 'campusppa')
            server.login(msg['From'], msg['To'], msg.as_string())
        return True
    except Exception as e:
        logger.error('exception @send_mail ->', e)
        return False