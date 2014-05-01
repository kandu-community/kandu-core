from django import template
from django.utils.safestring import mark_safe
import json
from collections import defaultdict

register = template.Library()

@register.inclusion_tag('web/visibility_dependencies_tag.html')
def visibility_dependencies_js(dependencies_dict):
	transponed_dict = defaultdict(lambda: defaultdict(list))
	for slave_input, terms in dependencies_dict.items():
		for master_input, value in terms.items():
			transponed_dict[master_input][value].append(slave_input)

	return { 'dependencies_dict': mark_safe(json.dumps(transponed_dict)) }