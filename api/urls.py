from django.conf.urls import url, patterns, include
from rest_framework.urlpatterns import format_suffix_patterns

import views

urlpatterns = patterns('',
    url(r'^getSubmissions/$', views.BaseFormList.as_view(), name='api_list'),
    url(r'^getSubmissions/(?P<model_name>\w+)/$', views.FormList.as_view(), name='api_list'),
    url(r'^getSubmissions/(?P<model_name>\w+)/(?P<pk>\d+)/$', views.FormDetail.as_view(), name='api_detail'),

    url(r'^get-token/$', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^browseable-auth/$', include('rest_framework.urls', namespace='rest_framework')) #for the browseable API
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])