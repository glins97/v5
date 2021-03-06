from django.contrib import admin
from django.utils.html import format_html
from .models import *
import os

def deactivate_themes(modeladmin, request, queryset):
    queryset.update(active=False)
deactivate_themes.short_description = "Desativar temas selecionados"

def activate_themes(modeladmin, request, queryset):
    queryset.update(active=True)
activate_themes.short_description = "Ativar temas selecionados"

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('description', 'active', 'arquivo_existe', 'jury', 'file')
    search_fields = ('description', )
    fieldsets = (
        ('Geral', {
            'fields': ('active', 'description', 'jury', 'axis', 'type', 'file', ),
        }),
        ('Tema da semana', {
            'fields': ('highlighted_start_date', 'highlighted_end_date', ),
        }),
    )
    actions = [activate_themes, deactivate_themes]

    def arquivo_existe(self, obj):
        # return True
        if os.path.exists(str(obj.file)):
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')

class EssayAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', )
    list_display = ('id', 'aluno', 'fn', 'tema', 'nota', )
    list_filter = ('theme', )
    autocomplete_fields = ('theme', )
    search_fields = ('user__first_name', 'user__last_name', 'theme__description')
    list_per_page = 100

    def fn(self, o):
        return format_html('<a href="/{fn}">{fn}</a>'.format(fn=o.file))

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
    list_display = ('codigo', 'jury', 'name', 'description', 'pai', 'nota', )
    list_filter = ('competency', 'jury')
    search_fields = ('name', 'competency', 'jury')
    list_per_page = 100

    def codigo(self, obj):
        return '{}'.format(obj.get_verbose_code())

    def pai(self, obj):
        return '{}'.format(obj.parent.get_verbose_code() if obj.parent else '-')

    def nota(self, obj):
        if obj.jury == 'ENEM':
            return '{}'.format(200 - obj.weight * 40)
        elif obj.jury == 'VUNESP':
            return '{}'.format(obj.weight)
        return '-'

class ErrorClassificationAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'jury', 'name', 'description', 'pai', 'nota', )
    list_filter = ('competency', 'jury')
    search_fields = ('name', 'competency', 'jury')
    list_per_page = 100

    def codigo(self, obj):
        return '{}'.format(obj.get_verbose_code())

    def pai(self, obj):
        return '{}'.format(obj.parent.get_verbose_code() if obj.parent else '-')
    
    def nota(self, obj):
        return '{}'.format(200 - obj.weight * 40)

class MentoringAdmin(admin.ModelAdmin):
    list_display = ('student', 'mentor', 'active')
    list_filter = ('mentor', 'active')
    search_fields = ('student', 'mentor', 'active')
    list_per_page = 100

class ExerciseListAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'file')
    search_fields = ('title', 'description',)
    list_per_page = 100

class InterestedExerciseListAdmin(admin.ModelAdmin):
    list_display = ('name', 'list', 'recommended', 'completed')
    list_filter = ('list', 'completed')
    search_fields = ('list', 'name')
    list_per_page = 100

    def name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def recommended(self, obj):
        return f'{obj.essay != None}'

admin.site.register(Theme, ThemeAdmin)
admin.site.register(Essay, EssayAdmin)
# admin.site.register(Profile)
admin.site.register(Correction, CorrectionAdmin)
admin.site.register(ErrorClassification, ErrorClassificationAdmin)
admin.site.register(GenericErrorClassification, GenericErrorClassificationAdmin)
# admin.site.register(Event)
admin.site.register(ExerciseList, ExerciseListAdmin)
admin.site.register(InterestedExerciseList, InterestedExerciseListAdmin)
admin.site.register(Notification)
admin.site.register(Mentoring, MentoringAdmin)
