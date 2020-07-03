from django.db import models
from django.contrib.auth.models import User

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

class TPS(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Matéria')
    week = models.CharField(max_length=255, choices=weeks, verbose_name='Semana')
    campus = models.CharField(max_length=255, choices=campi, verbose_name='Campus')
    start_date = models.DateTimeField(verbose_name='Início')
    end_date = models.DateTimeField(verbose_name='Término')
    max_questions = models.IntegerField(default=10, verbose_name='Número de questões')
    max_answers = models.IntegerField(default=40, verbose_name='Número de respostas')

    tbl = models.BooleanField(default=True, verbose_name="Produzir TBL")
    score_z = models.BooleanField(default=True, verbose_name="Produzir Score Z")
    distractor = models.BooleanField(default=True, verbose_name="Produzir Distrator")

    def __str__(self):
        return '{} {} {}'.format(self.campus, self.subject, self.week)

    class Meta:
        verbose_name = 'Formulário'
        verbose_name_plural = 'Formulários'

class Question(models.Model):
    tps = models.ForeignKey(TPS, on_delete=models.CASCADE)
    number = models.IntegerField()
    correct_answer = models.CharField(max_length=255, choices=answers)

    def __str__(self):
        return '{} {} {}'.format(self.tps, self.number, self.correct_answer)

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tps = models.ForeignKey(TPS, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True) 
    name = models.CharField(max_length=255)
    grade = models.IntegerField(default=0)
    q1 = models.CharField(max_length=1, choices=answers)
    q2 = models.CharField(max_length=1, choices=answers)
    q3 = models.CharField(max_length=1, choices=answers)
    q4 = models.CharField(max_length=1, choices=answers)
    q5 = models.CharField(max_length=1, choices=answers)
    q6 = models.CharField(max_length=1, choices=answers)
    q7 = models.CharField(max_length=1, choices=answers)
    q8 = models.CharField(max_length=1, choices=answers)
    q9 = models.CharField(max_length=1, choices=answers)
    q10 = models.CharField(max_length=1, choices=answers)

    def __str__(self):
        return '{}: {} {} {}'.format(self.name, self.tps.campus, self.tps.subject, self.tps.week)

    class Meta:
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'