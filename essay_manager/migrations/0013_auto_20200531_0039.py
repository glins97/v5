# Generated by Django 3.0.6 on 2020-05-31 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essay_manager', '0012_errorclassification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='errorclassification',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
