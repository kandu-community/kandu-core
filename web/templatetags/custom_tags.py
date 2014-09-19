from django import template
from django.utils.safestring import mark_safe
import json
from collections import defaultdict

from web.widgets import SearchForm

register = template.Library()

@register.inclusion_tag('web/visibility_dependencies_tag.html')
def visibility_dependencies_js(dependencies_dict, inline_prefix=None):
	transponed_dict = defaultdict(lambda: defaultdict(list))
	for slave_input, terms in dependencies_dict.items():
		for master_input, value in terms.items():
			transponed_dict[master_input][value].append(slave_input)

	return { 'dependencies_dict': mark_safe(json.dumps(transponed_dict)), 'inline_prefix': inline_prefix }

@register.inclusion_tag('web/search_form_tag.html')
def search_form():
	return {'search_form': SearchForm()}