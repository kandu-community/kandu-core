from django.contrib import admin

from models import Icon

class IconAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'partner_icon')

admin.site.register(Icon, IconAdmin)