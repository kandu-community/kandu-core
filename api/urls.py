from django.conf.urls import url, patterns, include
from rest_framework.urlpatterns import format_suffix_patterns

import views
import icons.views

urlpatterns = patterns('',
    url(r'^getConfig/$', views.DownloadConfig.as_view(), name='api_config'),
    url(r'^getForms/$', views.AvailableForms.as_view(), name='api_forms'),
    
    url(r'^getSubmissions/$', views.BaseFormList.as_view(), name='api_list'),
    url(r'^getSubmissions/(?P<model_name>\w+)/$', views.FormList.as_view(), name='api_list'),
    url(r'^getSubmissions/(?P<model_name>\w+)/(?P<pk>\d+)/$', views.FormDetail.as_view(), name='api_detail'),
    url(r'^getSubmissions/(?P<model_name>\w+)/search/?$', views.FormSearch.as_view(), name='api_search'),
    url(r'^getSubmissions/(?P<model_name>\w+)/inRadius/?$', views.FormInRadius.as_view(), name='api_in_radius'),

    url(r'^getIcons/$', icons.views.IconList.as_view(), name='api_icons'),

    url(r'^get-token/$', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^browseable-auth/$', include('rest_framework.urls', namespace='rest_framework')) #for the browseable API
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])