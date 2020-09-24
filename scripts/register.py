import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")
django.setup()

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
import codecs
from threading import _start_new_thread
def send_mail(email, subject, message, attachments='', multiple_attachments=False):
    msg = MIMEMultipart()
    password = 'campusppa'
    msg['To'] = email
    msg['From'] = 'adm.ppa.digital@gmail.com'
    msg['Subject'] = 'PPA Digital: ' + subject
    
    if not multiple_attachments:
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
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
    return True
from django.contrib.auth.models import Group
group = Group.objects.get(name='student')

import random
import string
import sys

def generate_ascii(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

from django.contrib.auth.models import User
students = []
with open('students.csv', 'r') as f:
    data = f.read().split('\n')
    for line in data:
        name, email, school, phone = line.split(',')
        user = User.objects.filter(username=email).first()
        if user:
            user.groups.add(group)
            user.save()
            print(f'user for {name} already exists')
        else:
            password = generate_ascii(9)
            print(f'creating new user for {name}')
            user = User.objects.create_user(email, email, password)
            user.groups.add(group)
            user.save()
            html = """
                <div style="background-color:#f7f7f7">  
                <div style="margin:0px auto;max-width:600px"> 
                    <table role="presentation" style="width:100%" cellspacing="0" cellpadding="0" border="0" align="center"> 
                    <tbody> 
                    <tr> 
                    <td style="direction:ltr;font-size:0px;padding:10px;padding-left:40px;padding-right:40px;text-align:center"></td> 
                    </tr> 
                    </tbody> 
                    </table> 
                </div> 
                <div style="border:1px solid #d9d9d9;background:white;background-color:white;margin:0px auto;max-width:600px"> 
                    <table role="presentation" style="background:white;background-color:white;width:100%" cellspacing="0" cellpadding="0" border="0" align="center"> 
                    <tbody> 
                    <tr> 
                    <td style="direction:ltr;font-size:0px;padding:20px 0;padding-bottom:30px;text-align:center"> 
                        <div style="margin:0px auto;max-width:600px"> 
                        
                        </div> 
                        <div style="background:#00bcd4;background-color:#00bcd4;margin:0px auto;max-width:600px"> 
                        <table role="presentation" style="background:#00bcd4;background-color:#00bcd4;width:100%" cellspacing="0" cellpadding="0" border="0" align="center"> 
                        <tbody> 
                        <tr> 
                            <td style="direction:ltr;font-size:0px;padding:20px 0;padding-left:40px;padding-right:40px;text-align:center"> 
                            <div class="m_6902621078980616255mj-column-per-100" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%"> 
                            <table role="presentation" style="vertical-align:top" width="100%" cellspacing="0" cellpadding="0" border="0"> 
                            <tbody> 
                                <tr> 
                                <td style="font-size:0px;padding:0px;word-break:break-word" align="center"> 
                                <div style="font-family:sans-serif;font-size:28px;line-height:150%;text-align:center;color:#ffffff"> <b>Registro realizado, {name}!</b> 
                                </div></td> 
                                </tr> 
                            </tbody> 
                            </table> 
                            </div></td> 
                        </tr> 
                        </tbody> 
                        </table> 
                        </div> 
                        <div style="margin:0px auto;max-width:600px"> 
                        <table role="presentation" style="width:100%" cellspacing="0" cellpadding="0" border="0" align="center"> 
                        <tbody> 
                        <tr> 
                            <td style="direction:ltr;font-size:0px;padding:40px 40px 0 40px;padding-left:40px;padding-right:40px;text-align:center"> 
                            <div class="m_6902621078980616255mj-column-per-100" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%"> 
                            <table role="presentation" style="vertical-align:top" width="100%" cellspacing="0" cellpadding="0" border="0"> 
                            <tbody> 
                                <tr> 
                                <td style="font-size:0px;padding:0px;word-break:break-word" align="center"> 
                                <div style="font-family:sans-serif;font-size:28px;line-height:250%;text-align:center;color:#00bcd4;">  
                                </div></td> 
                                </tr> 
                                <tr> 
                                <td style="font-size:0px;padding:0px;padding-bottom:20px;word-break:break-word" align="center"> 
                                <div style="font-family:sans-serif;font-size:16px;line-height:150%;text-align:center;color:#555555">Seu acesso à plataforma ppa.digital foi liberado! Parabéns.
                </div><div style="font-family:sans-serif;font-size:16px;line-height:150%;text-align:center;color:#555555">
                <br></div><div style="font-family:sans-serif;font-size:16px;line-height:150%;text-align:center;color:#555555">

                Agora, você já pode utilizar todos os recursos da plataforma para potencializar seu desempenho. Lembre-se de que você é seu maior concorrente e de que sua evolução depende, principalmente, da sua constância e da correção dos erros apontados. =)
                <br>
                <br>
                Aproveite o acesso aos temas de redação ENEM e VUNESP para desenvolver não só repertório sociocultural, mas também para estudar possíveis conteúdos sobre os quais você ainda não tem excelente domínio. Redação é método, é trabalho duro! #VagaSeConquista! #Seja+1OuSejaVC
                <br>
                <br>
                Seguem as credenciais de acesso:
                <br>
                Usuário: {user}
                <br>
                Senha: {password}
                <br>
                <br>
                Recomendamos que troque sua senha logo no primeiro login, na página de perfil.
                <br>
                <br>
                Por fim, quaisquer problemas e/ou sugestões podem ser reportados diretamente à nossa equipe pelo whatsapp ou enviados diretamente para este e-mail. 
                                </tr> 
                            </tbody> 
                            </table> 
                            </div></td> 
                        </tr> 
                        </tbody> 
                        </table> 
                        </div> 
                        <div style="margin:0px auto;max-width:600px"> 
                        <table role="presentation" style="width:100%" cellspacing="0" cellpadding="0" border="0" align="center"> 
                        <tbody> 
                        <tr> 
                            <td style="direction:ltr;font-size:0px;padding:20px 0;padding-bottom:0;padding-left:40px;padding-right:40px;text-align:center"> 
                            <div class="m_6902621078980616255mj-column-per-100" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%"> 
                            <table role="presentation" style="vertical-align:top" width="100%" cellspacing="0" cellpadding="0" border="0"> 
                            <tbody> 
                                <tr> 
                                <td style="font-size:0px;padding:0px;word-break:break-word" align="center"> 
                                <div style="font-family:sans-serif;font-size:16px;line-height:150%;text-align:center;color:#555555">
                                    Por enquanto, é isso! Bem-vindo e bons estudos! 
                                <br>Equipe PPA 
                                </div></td> 
                                </tr> 
                            </tbody> 
                            </table> 
                            </div></td> 
                        </tr> 
                        </tbody> 
                        </table> 
                        </div></td> 
                    </tr> 
                    </tbody> 
                    </table> 
                </div> 
                </div>
                """.format(name=name, user=email, password=password)
            send_mail(email, 'Acesso liberado!', html)