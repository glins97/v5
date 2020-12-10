import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")
django.setup()

from essay_manager.models import Essay
import requests
import time

def run():
    payload = {
        'username': 'glins',
        'password': 'qazxsaq01'
    }

    with requests.Session() as s:
        s.post('https://ppa.digital/api/login/', data=payload)
        
        essays = Essay.objects.filter(mailed=False, theme__jury='ENEM', grade__gt=0)
        for index, essay in enumerate(essays):
            if '@' not in essay.user.username: continue
            print(f'{index + 1} / {len(essays)}, #{essay.id} {essay.user.username}')
            r = s.get(f'https://ppa.digital/api/essays/mail/{essay.id}/')
