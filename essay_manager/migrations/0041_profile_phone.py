# Generated by Django 3.0.8 on 2020-08-12 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essay_manager', '0040_essay_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
