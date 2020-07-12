from django.contrib import admin
from .models import Theme, Essay, Profile, Correction, ErrorClassification, GenericErrorClassification

class EssayAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', )

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
admin.site.register(Correction)
admin.site.register(ErrorClassification, ErrorClassificationAdmin)
admin.site.register(GenericErrorClassification, GenericErrorClassificationAdmin)
