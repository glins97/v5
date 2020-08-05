from django.db import models
from django.contrib.auth.models import User

from pdf2image import pdfinfo_from_path, convert_from_path
import numpy as np
import PIL
from PIL import Image

import os
weeks = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
    ('24', '24'),
    ('25', '25'),
    ('26', '26'),
    ('27', '27'),
    ('28', '28'),
    ('29', '29'),
    ('30', '30'),
    ('31', '31'),
    ('32', '32'),
)

subjects = (
    ('BIO', 'BIO'),
    ('FIS', 'FIS'),
    ('QUI', 'QUI'),
    ('MAT', 'MAT'),
)
        
campi = (
    ('BSB', 'BRASÍLIA'),
    ('JUA', 'JUAZEIRO'),
    ('GOI', 'GOIANIA'),
)

answers = (
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
)

months = (
    ('1', 'Janeiro'),
    ('2', 'Fevereiro'),
    ('3', 'Março'),
    ('4', 'Maio'),
    ('5', 'Abril'),
    ('6', 'Junho'),
    ('7', 'Julho'),
    ('8', 'Agosto'),
    ('9', 'Setembro'),
    ('10', 'Outubro'),
    ('11', 'Novembro'),
    ('12', 'Dezembro'),
)

groups = (
    ('ENEM_ANUAL', 'ENEM ANUAL'),
    ('ENEM_SEMESTRAL', 'ENEM SEMESTRAL'),
    ('PARTICULARES', 'PARTICULARES'),
)

grade_groups = (
    ('SCORE_Z', 'SCORE_Z'),
    ('TBL', 'TBL'),
    ('CBT', 'CBT'),
)

class TPS(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Matéria')
    week = models.CharField(max_length=255, choices=weeks, verbose_name='Semana')
    campus = models.CharField(max_length=255, choices=campi, verbose_name='Campus')
    group = models.CharField(max_length=255, choices=groups, null=True, blank=True, verbose_name='Grupo')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Professor')
    start_date = models.DateTimeField(verbose_name='Início')
    end_date = models.DateTimeField(verbose_name='Término')
    max_questions = models.IntegerField(default=10, verbose_name='Número de questões')
    max_answers = models.IntegerField(default=40, verbose_name='Número de respostas')

    questions = models.FileField(upload_to='uploads', blank=True, null=True, verbose_name='Caderno de questões')
    solutions = models.FileField(upload_to='uploads', blank=True, null=True, verbose_name='Gabarito comentado')
    notify = models.BooleanField(default=True, verbose_name="Enviar ranking")

    def __str__(self):
        return '{} {} {}'.format(self.campus, self.subject, self.week)

    class Meta:
        verbose_name = 'Formulário'
        verbose_name_plural = 'Formulários'

    def save(self, *args, **kwargs):
        if not self.id:
            super(TPS, self).save(*args, **kwargs)

        directory = f'uploads/tps/{self.id}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        if self.questions and '.pdf' in str(self.questions.file).lower()[-4:]:
            super(TPS, self).save(*args, **kwargs)
            info = pdfinfo_from_path(str(self.questions.file), userpw=None, poppler_path=None)
            maxPages = info["Pages"]
            images = []
            for page in range(1, min(maxPages + 1, 10)) : 
                images.extend(convert_from_path(str(self.questions.file), dpi=200, first_page=page, last_page=page))

            min_shape = sorted( [(np.sum(i.size), i.size ) for i in images])[0][1]
            imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in images ) )
            imgs_comb = PIL.Image.fromarray( imgs_comb)
            
            destination = str(self.questions.file).lower().replace('.pdf', '.png')
            imgs_comb.save(str(self.questions.file).lower().replace('.pdf', '.png'))
            self.questions = destination.replace('/root/v5/', '')

        super(TPS, self).save(*args, **kwargs)

class Question(models.Model):
    tps = models.ForeignKey(TPS, on_delete=models.CASCADE)
    number = models.IntegerField()
    correct_answer = models.CharField(max_length=255, choices=answers)

    def __str__(self):
        return '{} {} {}'.format(self.tps, self.number, self.correct_answer)

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

class TPSAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tps = models.ForeignKey(TPS, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True) 
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    grade = models.IntegerField(default=0)
    mailed_results = models.BooleanField(default=False)
    mailed_answers = models.BooleanField(default=False)

    grade_group = models.CharField(max_length=255, choices=grade_groups, null=True, blank=True)
    grade_points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    accounted = models.BooleanField(default=False)
    
    def __str__(self):
        return '{}: {} {} {}'.format(self.name, self.tps.campus, self.tps.subject, self.tps.week)

    class Meta:
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'

    def save(self, *args, **kwargs):
        if not self.accounted and self.grade_group and self.rank:
            self.accounted = True
            
            if self.grade_group == 'SCORE_Z':
                self.grade_points = 3
            if self.grade_group == 'TBL':
                self.grade_points = 2
                if self.rank == 1:
                    self.grade_points = 3
            if self.grade_group == 'CBT':
                self.grade_points = 1
            
            score = TPSScore.objects.filter(group=self.tps.group, email=self.email, month=self.submission_date.month, campus=self.tps.campus).first()
            if score:
                score.score += self.grade_points
                score.save()
            else:
                TPSScore(group=self.tps.group, email=self.email, month=self.submission_date.month, campus=self.tps.campus, score=self.grade_points).save()

        super(TPSAnswer, self).save(*args, **kwargs)

class TPSScore(models.Model):
    email = models.CharField(max_length=255, null=True, blank=True)
    month = models.CharField(max_length=255, choices=months, null=True, blank=True)
    campus = models.CharField(max_length=255, choices=campi, null=True, blank=True)
    group = models.CharField(max_length=255, choices=groups, null=True, blank=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return '{} {}: {}, {}'.format(self.email, self.campus, self.month, self.score)

    class Meta:
        verbose_name = 'Pontuação'
        verbose_name_plural = 'Pontuações'

class QuestionAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    tps_answer = models.ForeignKey(TPSAnswer, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.CharField(max_length=255, choices=answers)
