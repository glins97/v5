# Generated by Django 3.0.3 on 2020-08-13 22:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('essay_manager', '0047_auto_20200812_1557'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theme',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='theme',
            name='start_date',
        ),
    ]
