import traceback
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")
django.setup()

from essay_manager.models import Theme
from random import choice
from datetime import datetime, timedelta

def set_weekly_themes(jury):
    themes = list(Theme.objects.filter(active=True, jury=jury, highlighted_start_date=None))
    date = datetime.now()
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    while themes and date.year == 2020:
        theme = choice(themes)
        themes.remove(theme)
        theme.highlighted_start_date = date
        date += timedelta(days=7) 
        theme.highlighted_end_date = date
        print(f'{theme.description} -> {theme.highlighted_start_date}')
        theme.save()

set_weekly_themes('ENEM')
set_weekly_themes('VUNESP')