# Generated by Django 3.0.4 on 2020-05-06 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essay_manager', '0003_correction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='essay',
            name='grade',
            field=models.IntegerField(default=0),
        ),
    ]
