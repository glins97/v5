from django.contrib import admin
from .models import Theme, Essay, Profile, Correction, ErrorClassification

class EssayAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', )

admin.site.register(Theme)
admin.site.register(Essay, EssayAdmin)
admin.site.register(Profile)
admin.site.register(Correction)
admin.site.register(ErrorClassification)
