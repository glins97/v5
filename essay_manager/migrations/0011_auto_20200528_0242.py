# Generated by Django 3.0.6 on 2020-05-28 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essay_manager', '0010_auto_20200527_2222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='correction',
            name='data',
            field=models.TextField(default='{}'),
        ),
    ]
