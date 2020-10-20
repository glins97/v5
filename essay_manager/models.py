from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from django.utils.timezone import now
import json 

from pdf2image import pdfinfo_from_path, convert_from_path
import numpy as np
import PIL
from PIL import Image

def  to_str(self, *args, **kwargs):
    return '{} {}'.format(self.first_name, self.last_name)
User.__str__ = to_str

juries = (
    ('ENEM', 'ENEM'),
    ('CESPE', 'CESPE'),
    ('VUNESP', 'VUNESP')
)

correction_statuses = (
    ('ACTIVE', 'ACTIVE'),
    ('DONE', 'DONE'),
)

theme_types = (
    ('FREE', 'SOLIDÁRIO'),
    ('PAID', 'PAGO'),
)

target_grades = (
    (800, 800),
    (900, 900),
    (1000, 1000),
)

essay_mode = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
)

productions = (
    ('2 por mês', '2 por mês'),
    ('1 por semana', '1 por semana'),
    ('2 por semana', '2 por semana'),
    ('3 por semana', '3 por semana'),
)

axes = (
    ('Saúde', 'Saúde'),
    ('Educação', 'Educação'),
    ('Política e Economia', 'Política e Economia'),
    ('Organização Social', 'Organização Social'),
    ('Meio Ambiente', 'Meio Ambiente'),
    ('Tecnologia', 'Tecnologia'),
    ('Outros Eixos', 'Outros Eixos'),
    ('De Outros Alunos', 'De Outros Alunos'),
)

class Theme(models.Model):
    active = models.BooleanField(default=False, verbose_name='Visível')
    description = models.CharField(max_length=255, verbose_name='Nome')
    jury = models.CharField(max_length=255, choices=juries, verbose_name='Banca')
    highlighted_start_date = models.DateTimeField(blank=True, null=True, verbose_name='Data de início')
    highlighted_end_date = models.DateTimeField(blank=True, null=True, verbose_name='Data de término')
    axis = models.CharField(max_length=255, choices=axes, default='OTHER', verbose_name='Eixo')
    file = models.FileField(upload_to='uploads/', verbose_name='Arquivo descritivo')
    type = models.CharField(default='PAID', choices=theme_types, max_length=255, verbose_name='Disponibilidade')
    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        if self.file and '.pdf' in str(self.file).lower()[-4:]:
            super(Theme, self).save(*args, **kwargs)
            info = pdfinfo_from_path(str(self.file.file), userpw=None, poppler_path=None)
            maxPages = info["Pages"]
            images = []
            for page in range(1, min(maxPages + 1, 10)) : 
                images.extend(convert_from_path(str(self.file.file), dpi=200, first_page=page, last_page=page))

            min_shape = sorted( [(np.sum(i.size), i.size ) for i in images])[0][1]
            imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in images ) )
            imgs_comb = PIL.Image.fromarray(imgs_comb)
            
            destination = str(self.file.file).lower().replace('.pdf', '.png')
            imgs_comb.save(str(self.file.file).lower().replace('.pdf', '.png'))
            self.file = destination.replace('/root/v5/', '')
            
        super(Theme, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'tema'
        verbose_name_plural = 'temas'
        
class Essay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    upload_date = models.DateField(auto_now_add=True)
    grade = models.IntegerField(default=0)
    mailed = models.BooleanField(default=False)
    nullified = models.BooleanField(default=False)
    mode = models.CharField(default='1', choices=essay_mode, max_length=255)

    def __str__(self):
        return '#{}, {}'.format(self.id, self.theme)

    def has_correction(self, status='DONE'):
        return Correction.objects.filter(essay=self, status=status).count() > 0

    def get_correction_status(self):
        self.correction_status = 'HOLD'
        if self.has_correction('DONE'):
            self.correction_status = 'DONE'
        elif self.has_correction('ACTIVE'):
            self.correction_status = 'ACTIVE'
        return self.correction_status

    def save(self, *args, **kwargs):
        if self.pk is None:
            mentoring = Mentoring.objects.filter(student=self.user, active=True).first()
            if mentoring:
                super(Essay, self).save(*args, **kwargs)
                Notification(user=mentoring.mentor, title=f'Nova redação do(a) {self.user.first_name}!', description='', href=f'/essays/{self.id}').save()
            
        if self.file:
            super(Essay, self).save(*args, **kwargs)
            if '.pdf' in str(self.file).lower()[-4:]:
                info = pdfinfo_from_path(str(self.file.file), userpw=None, poppler_path=None)
                maxPages = info["Pages"]
                images = []
                for page in range(1, min(maxPages + 1, 10)) : 
                    images.extend(convert_from_path(str(self.file.file), dpi=200, first_page=page, last_page=page))

                min_shape = sorted( [(np.sum(i.size), i.size ) for i in images])[0][1]
                imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in images ) )
                imgs_comb = PIL.Image.fromarray(imgs_comb)
                
                destination = str(self.file.file).lower().replace('.pdf', '.png')
                imgs_comb.save(str(self.file.file).lower().replace('.pdf', '.png'))
                self.file = destination.replace('/root/v5/', '')
        super(Essay, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Redação'
        verbose_name_plural = 'Redações'

class Correction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    essay = models.ForeignKey(Essay, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=correction_statuses, default='ACTIVE')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    data = models.TextField(default="{}")
    nullified = models.BooleanField(default=False, verbose_name='redação anulada')

    def __str__(self):
        return '{}, {} - {} {}, {}'.format(self.user, self.essay.id, self.essay.user.first_name, self.essay.user.last_name, self.essay.theme)

    def save(self, *args, **kwargs):
        if not self.data:
            self.data = '{}'

        if not self.start_date:
            self.start_date = now()
        self.end_date = now()        
            
        j_data = json.loads(self.data) 
        if self.data and j_data:
            self.essay.grade = 0
            for comp in j_data['competencies']['grades']:
                self.essay.grade += int(j_data['competencies']['grades'][comp])
            self.essay.save()

        if self.status == 'DONE':
            Notification(user=self.essay.user, title=f'Redação #{self.essay.id} corrigida!', description='', href=f'/essays/{self.essay.id}').save()
        #     from essay_manager.apis.essay import send_mail
        #     send_mail(self.essay.user, 'redação corrigida!', '<p>Acesse a plataforma para conferir a correção!</p>')

        super(Correction, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'correção'
        verbose_name_plural = 'correções'

competencies = (
    ('1', 'Competência 1'),
    ('2', 'Competência 2'),
    ('3', 'Competência 3'),
    ('4', 'Competência 4'),
    ('5', 'Competência 5'),
    ('a', 'Critério A'),
    ('b', 'Critério B'),
    ('c', 'Critério C'),
    ('0', 'Nota 0'),
)

class ErrorClassification(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True, default='')
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1023, blank=True, null=True)
    competency = models.CharField(max_length=255, default='1', choices=competencies)
    has_children = models.BooleanField(default=False, editable=False)
    parent = models.ForeignKey('ErrorClassification', on_delete=models.CASCADE, blank=True, null=True)
    p_parent = models.ForeignKey('ErrorClassification', on_delete=models.CASCADE, blank=True, null=True, related_name='previous_parent', editable=False)
    weight = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    target = models.CharField(default='comment-text', max_length=255)
    jury = models.CharField(default='VUNESP', choices=juries, max_length=255)

    def to_json(self):
        return json.drops({
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'parent': self.parent.to_json,
        })

    def verify_children(self):
        current_has_children = self.has_children
        objs = ErrorClassification.objects.filter(parent=self)
        if objs.count():
            self.has_children = True
        else:
            self.has_children = False
        if current_has_children != self.has_children:
            self.save()

    def get_verbose_code(self):
        return mark_safe('{}.{}'.format(self.parent.get_verbose_code() if self.parent else self.competency, self.code))

    def encapsulate_row(self, s):
        return mark_safe("""
        <div class="row" style="margin-left: 5px; margin-top: 7px;">
            {}
        </div>
        """.format(s))

    def leaf_checkbox_html(self):
        return mark_safe("""
        <div class="form-check col-sm">
            <label class="form-check-label">
                <input class="form-check-input" name="competencyError" type="checkbox" value="" id="ec-checkbox-{code}" onclick="updateTextfieldValue('ec-checkbox-{code}', '{target}', '{desc} ', 'c{competency}', {weight}, {apply})"> {name}
                <span class="form-check-sign">
                    <span class="check"></span>
                </span>
            </label>
        </div>
        """.format(
            code=self.get_verbose_code().replace('.', '-'),
            target=self.target,
            desc=self.description if self.description else '',
            name='{}'.format(self.name),
            competency=self.competency,
            weight=self.weight,
            apply='false'))
    
    def node_checkbox_html(self):
        return mark_safe("""
        <div class="form-check col-sm">
            <label class="form-check-label">
                <input class="form-check-input" name="competencyError" type="" value="" data-toggle="" data-target="#innerCheckboxes{code}"> {name}
                <div id="innerCheckboxes{code}" class="container">
                    {children}
                </div>
                <span class="card-icon">
                    <i class="material-icons">expand_more</i>
                </span>
            </label>
        </div>
        """.format(
            code=self.get_verbose_code().replace('.', '-'),
            desc=self.description if self.description else '',
            name='{}'.format(self.name),
            children='\n'.join([self.encapsulate_row(child.get_html()) for child in ErrorClassification.objects.filter(parent=self)])))

    def get_html(self):
        if not self.has_children:
            return self.leaf_checkbox_html()
        return self.node_checkbox_html()

    def save(self, *args, **kwargs):
        # if its parent (i.e parent not specified) and id also not specified 
        if not self.parent and not self.code:
            self.code = self.competency # id will be competency
        
        # updates parent status of has_children
        if self.parent:
            self.parent.verify_children()
        elif self.p_parent:
            self.p_parent.verify_children()

        # update previous parent to current one
        self.p_parent = self.parent
        super(ErrorClassification, self).save(*args, **kwargs)

    def __str__(self):
        return '{}.{} {}'.format(self.parent.get_verbose_code() if self.parent else self.competency, self.code, self.name) 

    class Meta:
        verbose_name = 'erro pontual'
        verbose_name_plural = 'erros pontuais'

class GenericErrorClassification(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True, default='')
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1023, blank=True, null=True)
    competency = models.CharField(max_length=255, default='a', choices=competencies)
    has_children = models.BooleanField(default=False, editable=False)
    parent = models.ForeignKey('GenericErrorClassification', on_delete=models.CASCADE, blank=True, null=True)
    p_parent = models.ForeignKey('GenericErrorClassification', on_delete=models.CASCADE, blank=True, null=True, related_name='gec_previous_parent', editable=False)
    weight = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    apply_on_select = models.BooleanField(default=True)
    target = models.CharField(default='formTextareaca', max_length=255)
    jury = models.CharField(default='VUNESP', choices=juries, max_length=255)

    def to_json(self):
        return json.drops({
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'parent': self.parent.to_json,
        })

    def verify_children(self):
        current_has_children = self.has_children
        objs = GenericErrorClassification.objects.filter(parent=self)
        if objs.count():
            self.has_children = True
        else:
            self.has_children = False
        if current_has_children != self.has_children:
            self.save()

    def get_verbose_code(self):
        return mark_safe('{}.{}'.format(self.parent.get_verbose_code() if self.parent else self.competency, self.code))

    def encapsulate_row(self, s):
        return mark_safe("""
        <div class="row" style="margin-left: 5px; margin-top: 7px;">
            {}
        </div>
        """.format(s))

    def leaf_checkbox_html(self):
        return mark_safe("""
        <div class="form-check col-sm">
            <label class="form-check-label">
                <input class="form-check-input" name="competencyError" type="checkbox" value="" id="gec-checkbox-{code}" onclick="updateTextfieldValue('gec-checkbox-{code}', '{target}', '{desc} ', 'c{competency}', {weight}, {apply})"> {name}
                <span class="form-check-sign">
                    <span class="check"></span>
                </span>
            </label>
        </div>
        """.format(
            code=self.get_verbose_code().replace('.', '-'),
            target=self.target,
            desc=self.description if self.description else '',
            name='({}) {}'.format(200 - self.weight * 40, self.name) if self.jury == 'ENEM' else '({}) {}'.format(self.weight, self.name),
            competency=self.competency,
            weight=self.weight,
            apply='true'))
    
    def node_checkbox_html(self):
        return mark_safe("""
        <div class="form-check col-sm">
            <label class="form-check-label">
                <input class="form-check-input" name="competencyError" type="" value="" data-toggle="collapse" data-target="#innerCheckboxes{code}"> {name}
                <div id="innerCheckboxes{code}" class="container collapse">
                    {children}
                </div>
                <span class="card-icon">
                    <i class="material-icons">expand_more</i>
                </span>
            </label>
        </div>
        """.format(
            code=self.get_verbose_code().replace('.', '-'),
            desc=self.description if self.description else '',
            name='{}'.format(self.name),
            children='\n'.join([self.encapsulate_row(child.get_html()) for child in GenericErrorClassification.objects.filter(parent=self)])))

    def get_html(self):
        if not self.has_children:
            return self.leaf_checkbox_html()
        return self.node_checkbox_html()

    def save(self, *args, **kwargs):
        # if its parent (i.e parent not specified) and id also not specified 
        if not self.parent and not self.code:
            self.code = self.competency # id will be competency
        
        # updates parent status of has_children
        if self.parent:
            self.parent.verify_children()
        elif self.p_parent:
            self.p_parent.verify_children()

        # update previous parent to current one
        self.p_parent = self.parent
        super(GenericErrorClassification, self).save(*args, **kwargs)

    def __str__(self):
        return '{}.{} {}'.format(self.parent.get_verbose_code() if self.parent else self.competency, self.code, self.name) 

    class Meta:
        verbose_name = 'erro de competência'
        verbose_name_plural = 'erros de competência'

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.CharField(max_length=255, default='PPA')
    target_grade = models.IntegerField(choices=target_grades, blank=True, null=True)
    target_production = models.CharField(max_length=255, choices=productions, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=255, blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)
    faculty = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name) 

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(default=-1)
    month = models.IntegerField(default=-1)
    day = models.IntegerField(default=-1)

    def __str__(self):
        return '{} {}, {}'.format(self.user.first_name, self.user.last_name, self.title) 

    class Meta:
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'

class ExerciseList(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return self.title 

    class Meta:
        verbose_name = 'exercício'
        verbose_name_plural = 'exercícios'

class InterestedExerciseList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(ExerciseList, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.completed and not self.completion_date:
            self.completion_date = now()
        super(InterestedExerciseList, self).save(*args, **kwargs)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    href = models.CharField(max_length=255, blank=True, null=True)
    received = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'notificação'
        verbose_name_plural = 'notificações'

class Mentoring(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentoring_student')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentoring_mentor')
    active = models.BooleanField(default=True)