# Generated by Django 3.0.4 on 2020-07-28 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tps', '0026_auto_20200728_2204'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tpsanswer',
            name='top_student',
        ),
        migrations.AddField(
            model_name='tpsanswer',
            name='rank',
            field=models.IntegerField(default=0),
        ),
    ]
