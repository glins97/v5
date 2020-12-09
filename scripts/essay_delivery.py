import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")
django.setup()

from essay_manager.models import Essay
import requests
import time

essays = Essay.objects.filter(mailed=False, theme__jury='ENEM')
for index, essay in enumerate(essays):
    print(f'{index + 1} / {len(essays)}, #{essay.id}')
    requests.get(f'https://ppa.digital/api/essays/mail/{essay.id}/')
    time.sleep(5)