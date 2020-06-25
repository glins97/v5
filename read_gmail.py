
import os, django
django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from django.contrib.auth.models import User
from essay_manager.models import Essay, Theme

import datetime
from time import time

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.settings.sharing',
]

import base64
from apiclient import errors

def get_bd_obj(class_, **kwargs):
    objs = class_.objects.all().filter(**kwargs)
    if objs: return objs[0]
    if class_ == User:
        users = list(User.objects.all().filter(username=kwargs['username']))
        if users:
            return users[0]
    obj = class_(**kwargs)
    obj.save()
    return obj

def get_attachments(service, msg_id, student):
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        for part in message['payload'].get('parts', ''):
            if part['filename']:    
                if 'data' in part['body']:
                    data=part['body']['data']
                else:
                    att_id=part['body']['attachmentId']
                    att=service.users().messages().attachments().get(userId='me', messageId=msg_id,id=att_id).execute()
                    data=att['data']

        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
        path = 'uploads/{}-{}'.format(time(), part['filename'])
        with open(path, 'wb') as f:
            f.write(file_data)
        return path
    except UnboundLocalError as error:
        print(repr(error))
        return None

def main():
    creds = None
    if os.path.exists('credentials/token'):
        with open('credentials/token', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('credentials/token', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        subject_ = ''
        from_email = ''
        from_name = ''
        attachment = None
        message_id = message['id']

        for header in msg['payload']['headers']:
            if header['name'] == 'From':
                if len(header['value'].split('<')) >= 2:
                    from_name, from_email = header['value'].split('<')
                    from_name = from_name.strip().upper()
                    from_email = from_email.replace('>', '')
                else:
                    from_name = 'UNKOWN NAME'
                    from_email = header['value'].replace('<', '').replace('>', '')
            if header['name'] == 'Subject':
                subject_ = header['value'].lower()
        from_name = from_name.replace('"', '').replace("'", '')
        
        blocks = ['GOOGLE']
        skip = False
        for block in blocks:
            if block in from_name:
                skip = True
        if skip: continue
        choice = input('{} {} (Y/N) '.format(from_name, subject_))
        if choice.lower() == 'y':
            first_name = ''
            last_name = ''
            if len(from_name.split()) >= 2:
                first_name = from_name.split()[0]
                last_name = from_name.split()[-1]
            student = get_bd_obj(User, username=from_email.lower(), first_name=first_name, last_name=last_name, password='ppadigital')
            theme = Theme.objects.get(description='Solidário 1')
            attachment = get_attachments(service, message_id, student)
            if attachment:
                essay = get_bd_obj(Essay, theme=theme, user=student, file=attachment)
                essay.save()

if __name__ == '__main__':
    main()