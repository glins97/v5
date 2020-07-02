from django.contrib import admin
from django.urls import include, path, re_path
from django.utils.html import format_html
from django.http import FileResponse
from django import forms

from tps.auxiliary import generate_score_z, generate_tbl, generate_distrator
from .models import TPS, Answer, Question

import subprocess

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tps', 'grade', )
    list_filter = ('tps', 'grade', )
    # search_fields = (,)
    list_per_page = 100

from django.contrib.admin.utils import flatten_fieldsets

def create_or_update(class_, **kwargs):
    search = class_.objects.filter(**kwargs) 
    if search.count():
        return search.get()
    obj = class_(**kwargs)
    obj.save()
    return obj

class TPSAdminForm(forms.ModelForm):
    class Meta:
        model = TPS
        exclude = ('', )

    def __init__(self, *args, **kwargs):
        super(TPSAdminForm, self).__init__(*args, **kwargs)
        questions = {i: 'NA' for i in range(1, 1000)}
        saved_questions = Question.objects.filter(tps__id=self.instance.id)
        for question in saved_questions:
            questions[question.number] = question.correct_answer

        for question_number in sorted(questions.keys()):
            self.fields[f'q{question_number}'] = forms.ChoiceField(choices=[('NA', 'NA'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], initial=questions[question_number])

    def save(self, commit=True):
        instance = super(TPSAdminForm, self).save(commit=False)
        print(repr(instance))
        for index, field in enumerate([attr for attr in self.cleaned_data if attr[0] == 'q']):
            if self.cleaned_data[field] != 'NA':
                # gets matching model or creates object if no matches exist 
                q = create_or_update(Question, tps=TPS.objects.get(id=instance.id), number=(index + 1))
                
                # updates only necessary questions, avoiding creation of duplicates
                if q.correct_answer != self.cleaned_data[field]: 
                    print(f'UPDATING FIELD {field}') 
                    q.correct_answer = self.cleaned_data[field]
                    q.save()

                # delete questions no longer used
                print(q.number, self.cleaned_data['max_questions'], q.number > self.cleaned_data['max_questions'])
                if q.number > self.cleaned_data['max_questions']:
                    q.delete() 
        if commit:
            instance.save()
        return instance

class TPSAdmin(admin.ModelAdmin):
    form = TPSAdminForm
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('subject', 'week', 'campus',),
        }),
        ('Informações', {
            'fields': ('max_answers', 'max_questions', 'tbl', 'score_z', 'distractor'),
        }),
        ('Data', {
            'fields': ('start_date', 'end_date',),
        }),
    )
    def get_form(self, request, obj=None, **kwargs):
        kwargs['fields'] =  flatten_fieldsets(self.fieldsets)
        return super(TPSAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(TPSAdmin, self).get_fieldsets(request, obj)
        newfieldsets = list(fieldsets)
        print(fieldsets)
        fields = [f'q{item}' for item in range(1, 1000)]
        newfieldsets.append(['Questões', { 'fields': fields }])
        return newfieldsets

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            '/static/tps/js/fields.js',
        )
    list_display = ('id', 'campus', 'subject', 'week', 'respostas', 'url', 'relatórios',)
    list_filter = ('campus', 'subject', 'week',)
    search_fields = ('campus', 'subject', 'week', )
    list_per_page = 20

    def url(self, obj):
        return 'ppa.digital/tps/{}/{}/{}/'.format(obj.campus.lower(), obj.subject.lower(), obj.week)
    
    def respostas(self, obj):
        return '{} / {}'.format(len(list(Answer.objects.filter(tps=obj))), obj.max_answers)

    def relatórios(self, obj):
        return format_html(
            '<a class="button" href="download/score_z/{}">Score Z</a>&nbsp'.format(obj.id) +
            '<a class="button" href="download/tbl/{}">TBL</a>&nbsp'.format(obj.id) +
            '<a class="button" href="download/distrator/{}">Distrator</a>&nbsp'.format(obj.id))

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'^download/score_z/(?P<id>[\w-]+)/$', self.download_pdf_score_z),
            re_path(r'^download/tbl/(?P<id>[\w-]+)/$', self.download_pdf_tbl),
            re_path(r'^download/distrator/(?P<id>[\w-]+)/$', self.download_pdf_distrator),
        ]
        return my_urls + urls

    def _gen_pdf(self, id, func):
        output = None
        fn = ''
        tps = TPS.objects.get(id=id)
        if func == 'score_z':
            fn = f'SCORE Z {tps}'
            output = generate_score_z(fn, id)
        if func == 'tbl':
            fn = f'TBL {tps}'
            output = generate_tbl(fn, id)
        if func == 'distrator':
            fn = f'DISTRATOR {tps}'
            output = generate_distrator(fn, id)
        
        subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', output, '--outdir', 'tps/outputs/pdfs'])
        return FileResponse(open(output.replace('xlsx', 'pdf'), 'rb'), as_attachment=True, filename=(fn + '.pdf'))

    def download_pdf_score_z(self, request, id):
        return self._gen_pdf(id, 'score_z')

    def download_pdf_tbl(self, request, id):
        return self._gen_pdf(id, 'tbl')

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

admin.site.register(Question, QuestionAdmin)
admin.site.register(TPS, TPSAdmin)
admin.site.register(Answer, AnswerAdmin)
