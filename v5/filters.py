import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logger = logging.getLogger('django')
def send_mail(message):
    try:
        msg = MIMEMultipart()
        password = 'campusppa'
        msg['To'] = 'gabriel.lins97@gmail.com'
        msg['From'] = 'adm.ppa.digital@gmail.com'
        msg['Subject'] = 'Error@PPA_Digital'

        msg.attach(MIMEText(message, 'html'))
        with smtplib.SMTP('smtp.gmail.com: 587') as server:
            server.starttls()
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        return True
    except Exception as e:
        logger.error(f'send_mail@filters::Failed to send mail | {e}')
        return False

def mail_errors(record):
    send_mail(str(record))
    return True