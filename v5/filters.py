import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
import logging
import traceback
from time import sleep
from threading import _start_new_thread

logger = logging.getLogger('django')
def send_mail():
    sleep(1)
    try:
        msg = MIMEMultipart()
        password = 'campusppa'
        msg['To'] = 'gabriel.lins97@gmail.com'
        msg['From'] = 'adm.ppa.digital@gmail.com'
        msg['Subject'] = 'Error@PPA_Digital'

        openedfile = None
        attachment = 'logs/error.log'
        with open(attachment, 'rb') as opened:
            openedfile = opened.read()
        attachedfile = MIMEApplication(openedfile, _subtype = "txt", _encoder=encode_base64)
        attachedfile.add_header('content-disposition', 'attachment', filename=attachment.split('/')[-1])
        msg.attach(attachedfile)

        with smtplib.SMTP('smtp.gmail.com: 587') as server:
            server.starttls()
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        return True
    except Exception as e:
        logger.warning(f'send_mail@filters::Failed to send mail | {e}')
        return False

def mail_errors(record):
    _start_new_thread(send_mail, ())
    return True