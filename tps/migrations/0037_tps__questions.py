# Generated by Django 3.0.3 on 2020-08-26 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tps', '0036_auto_20200808_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='tps',
            name='_questions',
            field=models.FileField(blank=True, editable=False, null=True, upload_to=''),
        ),
    ]
