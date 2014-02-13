from django.contrib import admin

from utils import get_form_models

for form_name, form_model in get_form_models():
	try:
		class FormAdmin(admin.ModelAdmin):
			list_display = form_model.label_fields

		admin.site.register(form_model, FormAdmin)
		
	except AttributeError:
		admin.site.register(form_model)