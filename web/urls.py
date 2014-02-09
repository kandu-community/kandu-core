from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from views import *

urlpatterns = patterns('',
    url(r'^$', login_required(FormList.as_view()), name='web_list'),
    url(r'^(?P<model_name>\w+)/create/', FormCreate.as_view(), name='web_create'),
    url(r'^(?P<model_name>\w+)/(?P<pk>\d+)/update/', FormUpdate.as_view(), name='web_update'),
    url(r'^(?P<model_name>\w+)/(?P<pk>\d+)/delete/', FormDelete.as_view(), name='web_delete'),

    url(r'^registration/', UserRegistration.as_view(), name='web_user_registration'),
    (r'^login/', 'django.contrib.auth.views.login', {'template_name': 'web/login.html'}),
    (r'^logout/', 'django.contrib.auth.views.logout', {'next_page': '/web/'}),

    url(r'^update-migrate/', 'web.views.update_and_migrate', name='web_update_and_migrate')
)