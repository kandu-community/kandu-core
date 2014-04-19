from forms.utils import get_form_models

def form_models(request):
	return { 'form_models': get_form_models(for_user=request.user) }