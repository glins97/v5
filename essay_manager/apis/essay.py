from essay_manager.decorators import login_required, has_permission
from django.shortcuts import redirect
from essay_manager.models import Theme, Essay, Correction
import logging

import logging
logger = logging.getLogger('django')

@login_required
def create_essay_endpoint(request):
    try:
        obj = request.FILES['file'] 
        fn = 'uploads/' + str(obj).split('/')[-1].replace(' ', '_')
        with open(fn, 'wb') as f:
            f.write(obj.file.read())
        theme = Theme.objects.get(description=request.POST['theme'])
        Essay(user=request.user, theme=theme, file=fn).save()
        return redirect('/essays/?added=True')
    except Exception as e:
        logger.error(f'create_essay_endpoint@essay::Exception thrown | {request.user} {request} {repr(e)}')
        return redirect('/essays/?added=False')
        

from essay_manager.apis.document import Document
from essay_manager.apis.pdf_filler import fill_pdf_fields
import subprocess
import json

@has_permission('monitor')
@login_required
def mail_essay_endpoint(request, id):
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

        # mail to final user
        mail_body = '<p>Sua redação corrigida se encontra em anexo! (ou, caso não, clique <a href="{}"> aqui</a>)<br>Para uma boa visualização, recomendamos abrir o arquivo com o Adobe Reader em um computador.</p>'.format('http://dev.ppa.digital/{}'.format(final_destination))
        if send_mail(str(essay.user.username), 'Redação corrigida!', mail_body, final_destination):
            essay.mailed = True
            essay.save()
            return redirect('/essays/?mailed=True')
        else:
            return redirect('/essays/?mailed=False')
    except Exception as e:
        print('exception', e)
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
        msg['From'] = 'adm.ppa.digital@gmail.com'
        msg['Subject'] = 'PPA Digital: ' + subject

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
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        return True
    except Exception as e:
        logger.error('exception @send_mail ->', e)
        return False