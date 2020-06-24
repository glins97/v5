from django.contrib import admin
from .models import TPS, Answer

class TPSAdmin(admin.ModelAdmin):
    list_display = ('id', 'campus', 'subject', 'week', 'url', 'relatórios',)
    list_filter = ('campus', 'subject', 'week',)
    search_fields = ('campus', 'subject', 'week', )
    list_per_page = 20

    def url(self, obj):
        return 'ppa.digital/tps/{}/{}/{}/'.format(obj.campus.lower(), obj.subject.lower(), obj.week)
    
    def relatórios(self, obj):
        return ''

admin.site.register(TPS, TPSAdmin)
admin.site.register(Answer)
