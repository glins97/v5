# Generated by Django 3.0.4 on 2020-07-29 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essay_manager', '0029_theme_axis'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
