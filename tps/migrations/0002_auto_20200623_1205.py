# Generated by Django 3.0.4 on 2020-06-23 15:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tps',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 23, 15, 5, 27, 176759, tzinfo=utc), verbose_name='Data de Término'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tps',
            name='max_students',
            field=models.IntegerField(default=40, verbose_name='Quantidade de alunos'),
        ),
        migrations.AddField(
            model_name='tps',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 23, 15, 5, 32, 875621, tzinfo=utc), verbose_name='Data de Início'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tps',
            name='campus',
            field=models.CharField(choices=[('BRASÍLIA', 'BRASÍLIA'), ('JUAZEIRO', 'JUAZEIRO'), ('GOIANIA', 'GOIANIA')], max_length=255, verbose_name='Campus'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q1',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 1'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q10',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 10'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q2',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 2'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q3',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 3'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q4',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 4'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q5',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 5'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q6',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 6'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q7',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 7'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q8',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 8'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='q9',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1, verbose_name='Questão 9'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='subject',
            field=models.CharField(choices=[('BIO', 'BIO'), ('FIS', 'FIS'), ('QUI', 'QUI'), ('MAT', 'MAT')], max_length=255, verbose_name='Matéria'),
        ),
        migrations.AlterField(
            model_name='tps',
            name='week',
            field=models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16')], max_length=255, verbose_name='Semana'),
        ),
    ]
