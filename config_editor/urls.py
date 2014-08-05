from django.conf.urls import patterns, url
# from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView

from views import *

urlpatterns = patterns('',
    url(r'^tree/$', TreeView.as_view(), name='get_tree'),
    url(r'^tree/(?P<config_file>\d+)/$', TreeView.as_view(), name='get_tree'),

    url(r'^node/$', NodeView.as_view(), name='get_node'),
    url(r'^node/(?P<custom_action>[\w_]+)/$', NodeView.as_view(), name='get_node'),

    url(r'^save/$', OverwriteConfig.as_view(), name='overwrite_config'),
    url(r'^reset/$', reset_changes, name='reset_changes'),

    url(r'^$', TemplateView.as_view(template_name='config_editor/complete_page.html'), name='complete_page')
)