from django.views.generic import View, TemplateView
from django.http import HttpResponse
from django.core.urlresolvers import reverse
import json

import utils


class JSONResponseMixin(object):
	def render_to_response(self, context):
		return self.get_json_response(self.convert_context_to_json(context))

	def get_json_response(self, content, **httpresponse_kwargs):
		return HttpResponse(content,
								 content_type='application/json',
								 **httpresponse_kwargs)

	def convert_context_to_json(self, context):
		return json.dumps(context)

class PythonRootMixin(object):
	def dispatch(self, *args, **kwargs):
		self.root = utils.get_root()
		return super(PythonRootMixin, self).dispatch(*args, **kwargs)

class TreeView(JSONResponseMixin, PythonRootMixin, View):
	def get(self, *args, **kwargs):
		return self.render_to_response(self.root.render_tree_json())

class NodeView(JSONResponseMixin, PythonRootMixin, View):
	def get(self, *args, **kwargs):
		node = self.root.find_by_id(str(self.request.GET['id']))
		return self.render_to_response({
			'schema': node.render_schema(),
			'data': node.render_data()
		})



