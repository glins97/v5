from django.contrib import admin
from django.utils.html import format_html
from .models import Theme, Essay, Profile, Correction, ErrorClassification, GenericErrorClassification

class EssayAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', )
    list_display = ('id', 'aluno', 'tema', 'nota', )
    list_filter = ('theme', )
    search_fields = ('user__first_name', 'user__last_name', 'theme__description')
    list_per_page = 100

    def aluno(self, o):
        return format_html(
            '<a href=/admin/auth/user/{}/change/>{}</a>'.format(
                o.user.id,
                o.user.first_name + ' ' + o.user.last_name))

    def tema(self, o):
        return o.theme.description

    def nota(self, o):
        return o.grade

class CorrectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_redacao', 'corretor', 'aluno', 'tema', 'status', 'nota', )
    list_per_page = 100
    search_fields = ('essay__user__first_name', 'essay__user__last_name', 'essay__theme__description')

    def id_redacao(self, o):
        return o.essay.id

    def corretor(self, o):
        return o.user.first_name + ' ' + o.user.last_name 

    def aluno(self, o):
        return format_html(
            '<a href=/admin/auth/user/{}/change/>{}</a>'.format(
                o.essay.user.id,
                o.essay.user.first_name + ' ' + o.essay.user.last_name))

    def tema(self, o):
        return o.essay.theme.description

    def nota(self, o):
        return o.essay.grade

class GenericErrorClassificationAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'name', 'pai', 'nota', )
    list_filter = ('competency', )
    search_fields = ('name', 'competency')
    list_per_page = 20

    def codigo(self, obj):
        return '{}'.format(obj.get_verbose_code())

    def pai(self, obj):
        return '{}'.format(obj.parent.get_verbose_code() if obj.parent else '-')

    def nota(self, obj):
        return '{}'.format(200 - obj.weight * 40)

class ErrorClassificationAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'name', 'pai', 'nota', )
    list_filter = ('competency', )
    search_fields = ('name', 'competency')
    list_per_page = 20

    def codigo(self, obj):
        return '{}'.format(obj.get_verbose_code())

    def pai(self, obj):
        return '{}'.format(obj.parent.get_verbose_code() if obj.parent else '-')
    
    def nota(self, obj):
        return '{}'.format(200 - obj.weight * 40)

admin.site.register(Theme)
admin.site.register(Essay, EssayAdmin)
admin.site.register(Profile)
admin.site.register(Correction, CorrectionAdmin)
admin.site.register(ErrorClassification, ErrorClassificationAdmin)
admin.site.register(GenericErrorClassification, GenericErrorClassificationAdmin)
