# Generated by Django 3.0.6 on 2020-05-17 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essay_manager', '0007_profile_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='correction',
            name='upload_date',
            field=models.DateField(auto_now=True),
        ),
    ]
