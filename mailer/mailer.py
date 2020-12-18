import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
import codecs
from threading import _start_new_thread

import logging
logger = logging.getLogger('django')

def send_templated_mail(template, to, subject, attachments=[], *args, **kwargs):
    try:
        src = ''
        with open(f'mailer/templates/{template}') as f:
            src = f.read().format(*args, **kwargs)
        try:
            send_mail(to, subject, src, attachments)
        except Exception as e:
            logger.error(f'mailer@send_mail::Exception thrown | {template} {to} {subject} {attachments} {args} {kwargs} {repr(e)}')
            return False
    except Exception as e:
        logger.error(f'mailer@template_loader::Exception thrown | {template} {to} {subject} {attachments} {args} {kwargs} {repr(e)}')
        return False
    return True

def send_mail(to, subject, message, attachments=''):
    msg = MIMEMultipart()
    msg['To'] = to
    msg['Subject'] = subject
    msg['From'] = 'PPA <contato@ppa.digital>'
    
    if type(attachments) != list:
        attachments = [attachments]

    for attachment in attachments:
        if not attachment: continue
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
        server.sendmail(msg['From'], msg['To'], msg.as_string())
    return True