from django import forms
import autocomplete_light
import itertools

from forms.utils import get_search_fields, get_form_models, search_in_queryset

class SearchAutocomplete(autocomplete_light.AutocompleteGenericBase):
	choices = []
	search_fields = []

	def choices_for_request(self):
		q = self.request.GET.get('q', '')

		request_choices = itertools.chain(*(
			search_in_queryset(queryset=form_class.objects.all(), search_query=q, limit=40)
			for form_name, form_class in get_form_models(for_user=self.request.user)
		))

		return request_choices

autocomplete_light.register(SearchAutocomplete)

class SearchForm(forms.Form):
	query = forms.CharField(widget=autocomplete_light.TextWidget('SearchAutocomplete'))

class DatepickerWidget(forms.DateInput):
	'''
	Uses jQuery UI datepicker (included in SmartAdmin).
	'''

	def render(self, name, value, attrs=None):
		attrs['data-datepicker'] = 'yes'
		return super(DatepickerWidget, self).render(name, value, attrs)