from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^$', FormList.as_view(), name='web_list'),
    url(r'^(?P<model_name>\w+)/create/$', FormCreate.as_view(), name='web_create'),
    url(r'^(?P<model_name>\w+)/(?P<pk>\d+)/update/$', FormUpdate.as_view(), name='web_update'),
    url(r'^(?P<model_name>\w+)/(?P<pk>\d+)/delete/$', FormDelete.as_view(), name='web_delete')
)