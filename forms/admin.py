from django.contrib import admin

from utils import get_form_models

for form_name, form_model in get_form_models():
	admin.site.register(form_model)
