from django.contrib import admin
from django.urls import include, path, re_path
from django.utils.html import format_html
from django.http import FileResponse
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter

from datetime import date
import subprocess

from tps.auxiliary import generate_score_z, generate_tbl, generate_cbt, generate_distrator
from .models import TPS, TPSAnswer, TPSScore, Question, QuestionAnswer

class TPSScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'campus', 'group', 'month', 'score',)
    list_filter = ('month', 'campus', 'group',)
    list_per_page = 40

def resend_results(modeladmin, request, queryset):
    queryset.update(mailed_results=False)
resend_results.short_description = "Reenviar resultados"

def resend_answers(modeladmin, request, queryset):
    queryset.update(mailed_answers=False)
resend_answers.short_description = "Reenviar respostas"

class TPSAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'submission_date', 'tps', 'grade',)
    list_filter = ('tps', 'grade',)
    search_fields = ('tps__subject', 'name', 'email', )
    list_per_page = 100
    actions = [resend_results, resend_answers]

from django.contrib.admin.utils import flatten_fieldsets

def create_or_update(class_, **kwargs):
    search = class_.objects.filter(**kwargs) 
    if search.count():
        return search.get()
    obj = class_(**kwargs)
    obj.save()
    return obj

class SubjectFilter(SimpleListFilter):
    title = 'matéria'
    parameter_name = 'matéria'

    def lookups(self, request, model_admin):
        return [
            ('BIO', 'BIO'),
            ('FIS', 'FIS'),
            ('GEO', 'GEO'),
            ('HIST', 'HIST'),
            ('MAT', 'MAT'),
            ('QUI', 'QUI'),
        ]

    def queryset(self, request, queryset):
        objs = []
        if self.value() == 'BIO':
            for obj in queryset:
                if 'bio' in obj.subject.lower():
                    objs.append(obj.id)
        if self.value() == 'FIS':
            for obj in queryset:
                if 'fis' in obj.subject.lower() or 'fís' in obj.subject.lower():
                    objs.append(obj.id)
        if self.value() == 'GEO':
            for obj in queryset:
                if 'geo' in obj.subject.lower():
                    objs.append(obj.id)
        if self.value() == 'HIST':
            for obj in queryset:
                if 'hist' in obj.subject.lower():
                    objs.append(obj.id)
        if self.value() == 'MAT':
            for obj in queryset:
                if 'mat' in obj.subject.lower():
                    objs.append(obj.id)
        if self.value() == 'QUI':
            for obj in queryset:
                if 'qui' in obj.subject.lower() or 'quí' in obj.subject.lower():
                    objs.append(obj.id)
        if self.value():
            return TPS.objects.filter(id__in=objs)
        return TPS.objects.all()

class TPSAdminForm(forms.ModelForm):
    class Meta:
        model = TPS
        exclude = ('', )

    def __init__(self, *args, **kwargs):
        super(TPSAdminForm, self).__init__(*args, **kwargs)
        questions = {i: 'NA' for i in range(1, 121)}
        saved_questions = Question.objects.filter(tps__id=self.instance.id)
        for question in saved_questions:
            questions[question.number] = question.correct_answer

        for question_number in range(1, 121):
            self.fields[f'q{question_number}'] = forms.ChoiceField(choices=[('NA', 'NA'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('ANULADA', 'ANULADA')], initial=questions[question_number])
        
    def save(self, commit=True):
        instance = super(TPSAdminForm, self).save(commit=False)
        instance.save()

        for index in range(1, 121):
            field = f'q{index}'
            if self.cleaned_data[field] != 'NA':
                # gets matching model or creates object if no matches exist 
                q = create_or_update(Question, tps=TPS.objects.get(id=instance.id), number=index)
                
                # updates only necessary questions, avoiding creation of duplicates
                if q.correct_answer != self.cleaned_data[field]: 
                    q.correct_answer = self.cleaned_data[field]
                    q.save()

                # delete questions no longer used
                if q.number > self.cleaned_data['max_questions']:
                    q.delete() 
        if commit:
            instance.save()
        return instance

def duplicate_tps(modeladmin, request, queryset):
    for tps in queryset:
        t_copy = TPS(
            subject=tps.subject,
            week=tps.week,
            campus=tps.campus,
            group=tps.group,
            teacher=tps.teacher,
            start_date=tps.start_date,
            end_date=tps.end_date,
            max_questions=tps.max_questions,
            max_answers=tps.max_answers,
            questions=tps.questions,
            solutions=tps.solutions,
            notify=tps.notify,
            separate=tps.separate,
            mailed=tps.mailed,
        )
        t_copy.save()
        for question in Question.objects.filter(tps=tps):
            q_copy = Question(
                tps=t_copy,
                number=question.number,
                correct_answer=question.correct_answer
            )
            q_copy.save()
duplicate_tps.short_description = "Duplicar formulários selecionados"

class TPSAdmin(admin.ModelAdmin):
    form = TPSAdminForm
    actions = [duplicate_tps]
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('subject', 'week', 'questions', 'solutions', ),
        }),
        ('Informações', {
            'fields': ('campus', 'group', 'teacher', 'max_answers', 'max_questions', 'separate',),
        }),
        ('Data', {
            'fields': ('start_date', 'end_date', ),
        }),
    )
    
    def render_change_form(self, request, context, *args, **kwargs):
        teachers = [user.id for user in User.objects.filter() if user.groups.filter(name='tps-teachers').exists()]
        context['adminform'].form.fields['teacher'].queryset = User.objects.filter(id__in=teachers)
        return super(TPSAdmin, self).render_change_form(request, context, *args, **kwargs)

    def render_add_form(self, request, context, *args, **kwargs):
        teachers = [user.id for user in User.objects.filter() if user.groups.filter(name='tps-teachers').exists()]
        context['adminform'].form.fields['teacher'].queryset = User.objects.filter(id__in=teachers)
        return super(TPSAdmin, self).render_add_form(request, context, *args, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['fields'] =  flatten_fieldsets(self.fieldsets)
        return super(TPSAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(TPSAdmin, self).get_fieldsets(request, obj)
        newfieldsets = list(fieldsets)
        fields = [f'q{item}' for item in range(1, 121)]
        newfieldsets.append(['Questões', { 'fields': fields }])
        return newfieldsets

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            '/static/tps/js/fields.js',
        )
    list_display = ('id', 'campus', 'subject', 'week', 'respostas', 'end_date', 'url', 'arquivos', 'relatórios',)
    list_filter = ('campus', 'end_date', SubjectFilter)
    search_fields = ('campus', 'subject', 'week', )
    list_per_page = 20

    def url(self, obj):
        return 'ppa.digital/tps/{}/{}/'.format(obj.id, obj.campus.lower())
    
    def respostas(self, obj):
        return '{} / {}'.format(TPSAnswer.objects.filter(tps=obj).count(), obj.max_answers)

    def arquivos(self, obj):
            return format_html(''.join(
                [f'<a class="button" href="/{obj.original_questions if obj.original_questions else obj.questions}">CADERNO</a>&nbsp', f'<a class="button" href="/{obj.solutions}">GABARITO</a>&nbsp']
            ))

    def relatórios(self, obj):
        all_buttons = {
            'SCORE_Z': '<a class="button" href="download/score_z/{}">Score Z</a>&nbsp'.format(obj.id),
            'TBL': '<a class="button" href="download/tbl/{}">TBL</a>&nbsp'.format(obj.id),
            'CBT': '<a class="button" href="download/cbt/{}">CBT</a>&nbsp'.format(obj.id),
            'DISTRATOR': '<a class="button" href="download/distrator/{}">Distrator</a>&nbsp'.format(obj.id),
        }
        available_buttons = []
        if TPSAnswer.objects.filter(tps=obj).count():
            if obj.separate:
                if obj.campus == 'BSB':
                    if obj.group == 'PARTICULARES':
                        available_buttons = [all_buttons['TBL'], all_buttons['CBT']]
                    else:
                        available_buttons = [all_buttons['SCORE_Z'], all_buttons['TBL'], all_buttons['CBT']]
                else:
                    available_buttons = [all_buttons['SCORE_Z'], all_buttons['TBL']]
            available_buttons += [all_buttons['DISTRATOR']]
            return format_html(''.join(available_buttons))
        return 'Aguarde a primeira resposta'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'^download/score_z/(?P<id>[\w-]+)/$', self.download_pdf_score_z),
            re_path(r'^download/tbl/(?P<id>[\w-]+)/$', self.download_pdf_tbl),
            re_path(r'^download/cbt/(?P<id>[\w-]+)/$', self.download_pdf_cbt),
            re_path(r'^download/distrator/(?P<id>[\w-]+)/$', self.download_pdf_distrator),
        ]
        return my_urls + urls

    def _gen_pdf(self, id, func):
        output = None
        tps = TPS.objects.get(id=id)
        if func == 'score_z':
            output = generate_score_z(tps)
        if func == 'tbl':
            output = generate_tbl(tps)
        if func == 'cbt':
            output = generate_cbt(tps)
        if func == 'distrator':
            output = generate_distrator(tps)
        
        subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', output, '--outdir', 'tps/outputs/pdfs'])
        return FileResponse(open(output.replace('xlsx', 'pdf'), 'rb'), as_attachment=True, filename=(func.upper() + '.pdf'))

    def download_pdf_score_z(self, request, id):
        return self._gen_pdf(id, 'score_z')

    def download_pdf_tbl(self, request, id):
        return self._gen_pdf(id, 'tbl')

    def download_pdf_cbt(self, request, id):
        return self._gen_pdf(id, 'cbt')

    def download_pdf_distrator(self, request, id):
        return self._gen_pdf(id, 'distrator')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('tps_id', 'campus', 'subject', 'week', 'questão', 'correct_answer', )
    list_filter = ('tps__subject', 'tps__campus', )
    search_fields = ('tps', 'q', 'tps__subject', 'tps__campus', )
    list_per_page = 100

    def tps_id(self, obj):
        return obj.tps.id

    def campus(self, obj):
        return obj.tps.campus
    
    def subject(self, obj):
        return obj.tps.subject

    def week(self, obj):
        return obj.tps.week

    def questão(self, obj):
        return 'Questão {}'.format(obj.number)

class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('tps', 'answer_id', 'user', 'question', 'correct_answer', 'answer')
    search_fields = ('tps_answer__email', )
    list_per_page = 100

    def tps(self, obj):
        return obj.question.tps

    def answer_id(self, obj):
        return obj.tps_answer.id

    def user(self, obj):
        return obj.tps_answer.name + ' ' + obj.tps_answer.email

    def correct_answer(self, obj):
        return obj.question.correct_answer

admin.site.register(QuestionAnswer, QuestionAnswerAdmin)
# admin.site.register(Question, QuestionAdmin)
admin.site.register(TPS, TPSAdmin)
admin.site.register(TPSAnswer, TPSAnswerAdmin)
admin.site.register(TPSScore, TPSScoreAdmin)
