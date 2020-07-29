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
    mailed = models.BooleanField(default=False)

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
