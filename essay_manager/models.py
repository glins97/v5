from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from pdf2image import convert_from_path
from django.utils.timezone import now
import json 

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

class Theme(models.Model):
    description = models.CharField(max_length=255)
    jury = models.CharField(max_length=255, choices=juries)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    auxilliary_text = models.TextField()
    type = models.CharField(default='PAID', choices=theme_types, max_length=255)
    def __str__(self):
        return self.description

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

    def __str__(self):
        return '#{} - {} {}, {} => {}'.format(self.id, self.user.first_name, self.user.last_name, self.theme, self.file)

    def save(self, *args, **kwargs):
        if self.file:
            super(Essay, self).save(*args, **kwargs)
            if self.file.name[-4:].lower() == '.pdf':
                destination = self.file.name.split(self.file.name[-4:])[0] + '.PNG'
                convert_from_path(self.file.name, 300)[0].save(destination, 'PNG')
                self.file = destination
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
        """.format(code=self.get_verbose_code().replace('.', '-'), target=self.target, desc=self.description if self.description else '', name='{} {}'.format(self.get_verbose_code(), self.name), competency=self.competency, weight=self.weight, apply='false'))
    
    def node_checkbox_html(self):
        return mark_safe("""
        <div class="form-check col-sm">
            <label class="form-check-label">
                <input class="form-check-input" name="competencyError" type="" value="" data-toggle="" data-target="#innerCheckboxes{code}"> {name}
                <div id="innerCheckboxes{code}" class="container">
                    {children}
                </div>
            </label>
        </div>
        """.format(code=self.get_verbose_code().replace('.', '-'), desc=self.description if self.description else '', name='{} {}'.format(self.get_verbose_code(), self.name), children='\n'.join([self.encapsulate_row(child.get_html()) for child in ErrorClassification.objects.filter(parent=self)])))

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
    competency = models.CharField(max_length=255, default='1', choices=competencies)
    has_children = models.BooleanField(default=False, editable=False)
    parent = models.ForeignKey('GenericErrorClassification', on_delete=models.CASCADE, blank=True, null=True)
    p_parent = models.ForeignKey('GenericErrorClassification', on_delete=models.CASCADE, blank=True, null=True, related_name='gec_previous_parent', editable=False)
    weight = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    apply_on_select = models.BooleanField(default=False)
    target = models.CharField(default='formTextareac1', max_length=255)

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
        """.format(code=self.get_verbose_code().replace('.', '-'), target=self.target, desc=self.description if self.description else '', name='{} {}'.format(self.get_verbose_code(), self.name), competency=self.competency, weight=self.weight, apply='true'))
    
    def node_checkbox_html(self):
        return mark_safe("""
        <div class="form-check col-sm">
            <label class="form-check-label">
                <input class="form-check-input" name="competencyError" type="" value="" data-toggle="collapse" data-target="#innerCheckboxes{code}"> {name}
                <div id="innerCheckboxes{code}" class="container collapse">
                    {children}
                </div>
            </label>
        </div>
        """.format(code=self.get_verbose_code().replace('.', '-'), desc=self.description if self.description else '', name='{} {}'.format(self.get_verbose_code(), self.name), children='\n'.join([self.encapsulate_row(child.get_html()) for child in GenericErrorClassification.objects.filter(parent=self)])))

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
    email = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=255, blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)
    faculty = models.CharField(max_length=255, blank=True, null=True)