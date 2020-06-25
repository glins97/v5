from django.contrib import admin
from django.urls import include, path, re_path
from django.utils.html import format_html
from django.http import FileResponse
from tps.auxiliary import generate_score_z, generate_tbl, generate_distrator
from .models import TPS, Answer

import subprocess

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tps', 'grade', )
    list_filter = ('tps', 'grade', )
    # search_fields = (,)
    list_per_page = 100
 
class TPSAdmin(admin.ModelAdmin):
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


admin.site.register(TPS, TPSAdmin)
admin.site.register(Answer, AnswerAdmin)
