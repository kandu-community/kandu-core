from django.views.generic import View, TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import json

import utils
from forms import misc


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
		
		response = super(PythonRootMixin, self).dispatch(*args, **kwargs)

		if self.request.method.lower() in ['put', 'post', 'delete']:
			utils.save_root(self.root)

		return response

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

	def put(self, *args, **kwargs):
		node = self.root.find_by_id(str(self.request.GET['id']))
		json_object = json.loads(self.request.body)

		if self.kwargs.has_key('custom_action') and self.kwargs['custom_action'] == 'change_field_type':
			node.parent_form().change_field_type(node, json_object['type'])
		else:
			node.load_data(json_object)
	
		return self.render_to_response({'result': 'ok', 'node_id': node._id})

	def post(self, *args, **kwargs):
		node_type = self.request.GET['nodeType']
		if node_type == 'form':
			new_node = self.root.insertChild()
		elif node_type == 'field':
			parent_node = self.root.find_by_id(self.request.GET['id']).parent_form()
			new_node = parent_node.insertChild()
		elif node_type == 'inline':
			parent_node = self.root.find_by_id(self.request.GET['id']).parent_form()
			new_node = parent_node._inlines_container.insertChild()
		elif node_type == 'condition':
			parent_node = self.root.find_by_id(self.request.GET['id'])
			new_node = parent_node.insertChild()

		return self.render_to_response({'result': 'ok', 'node_id': new_node._id})

	def delete(self, *args, **kwargs):
		node = self.root.find_by_id(str(self.request.GET['id']))
		node.parent().removeChildren(node)
		return self.render_to_response({'result': 'ok'})

def reset_changes(request):
	utils.reset_changes()
	return HttpResponseRedirect(reverse('editor:complete_page'))

class OverwriteConfig(PythonRootMixin, View):
	def get(self, *args, **kwargs):
		utils.save_to_config(self.root)
		return HttpResponseRedirect(reverse('editor:complete_page'))