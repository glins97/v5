
# import os, django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")
# django.setup()

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from django.contrib.auth.models import User
from essay_manager.models import Essay, Theme

import datetime
from dateutil import parser
from time import time

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.settings.sharing',
]

START_DATE = datetime.datetime(year=2020, month=12, day=9, tzinfo=datetime.timezone.utc) 

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
        path = 'uploads/{}_{}'.format(time(), part['filename'])
        with open(path, 'wb') as f:
            f.write(file_data)
        return path
    except UnboundLocalError as error:
        print(repr(error))
        return None

def run():
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
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=200).execute()
    messages = results.get('messages', [])

    # results = service.users().messages().list(userId='me', labelIds=['INBOX'], page).execute()
    print(len(messages))
    print(results.keys())

    for index, message in enumerate(messages[-90::-1]):
        print(index)
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        subject_ = ''
        from_email = ''
        from_name = ''
        attachment = None
        message_id = message['id']

        skip = False
        date = None
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
            
            if header['name'] == 'Date':
                date = parser.parse(header['value'])
                if date < START_DATE:
                    skip = True

        from_name = from_name.replace('"', '').replace("'", '')
        
        blocks = ['GOOGLE', 'MAIL DELIVERY', 'acesso', 'teste']
        skip = skip or False
        for block in blocks:
            if block in from_name or block in subject_:
                skip = True
        # print('{} {} {} (Y/N) '.format(from_name, date, subject_))
        if skip: continue
        choice = input('{} {} {} (Y/N) '.format(from_name, date, subject_))
        if choice.lower() == 'y':
            first_name = ''
            last_name = ''
            if len(from_name.split()) >= 2:
                first_name = from_name.split()[0]
                last_name = from_name.split()[-1]
            student = get_bd_obj(User, username=from_email.lower(), first_name=first_name, last_name=last_name, password='ppadigital')
            theme = Theme.objects.get(description='Solidário')
            attachment = get_attachments(service, message_id, student)
            if attachment:
                essay = Essay(theme=theme, user=student, file=attachment, upload_date=date)
                essay.save()

