from django.utils.functional import SimpleLazyObject

from models import Icon

def icons(request):
	return {
		'logo': Icon.objects.filter(partner_icon=True).first(),
		'other_logos': Icon.objects.filter(partner_icon=False)
	}