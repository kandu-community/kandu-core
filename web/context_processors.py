from forms.utils import get_form_models
from collections import OrderedDict

def form_models(request):
	# return { 'form_models': [ (category, list(models)) for category, models in groupby( get_form_models(for_user=request.user), key=lambda (name,model): model.category ) ] }
	# return { 'form_models': get_form_models(for_user=request.user) }
	categories_dict = OrderedDict()
	for name, model in get_form_models(for_user=request.user):
		if not categories_dict.has_key(model.category):
			categories_dict[model.category] = []

		categories_dict[model.category].append((name, model))

	return {'categories_dict': categories_dict}