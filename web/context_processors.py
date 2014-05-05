from forms.utils import get_form_models
from itertools import groupby

def form_models(request):
	# return { 'form_models': [ (category, list(models)) for category, models in groupby( get_form_models(for_user=request.user), key=lambda (name,model): model.category ) ] }
	return { 'form_models': [form_model for form_name, form_model in get_form_models(for_user=request.user)] }