from django.contrib import admin
from django.db.models import ManyToManyField
import autocomplete_light

from utils import get_form_models, get_search_fields

for form_name, form_model in get_form_models():
    try:
            class FormAdmin(admin.ModelAdmin):
                    list_display = [field.name for field in form_model._meta.fields if field.name in form_model.label_fields and not isinstance(field, ManyToManyField)] + [ 'user', 'created_at' ]
                    search_fields = get_search_fields(form_model)

            admin.site.register(form_model, FormAdmin)
            
    except AttributeError:
            admin.site.register(form_model)

    autocomplete_light.register(form_model, search_fields=get_search_fields(form_model))
