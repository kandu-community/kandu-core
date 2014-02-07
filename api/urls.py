from django.conf.urls import url, patterns, include

import views

urlpatterns = patterns('',
    url(r'^', views.FormList.as_view(), name='api_list'),
    url(r'^(?P<model_name>\w+)/', views.FormList.as_view(), name='api_list'),
    url(r'^(?P<model_name>\w+)/(?P<pk>\d+)/', views.FormDetail.as_view(), name='api_detail'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')) #for the browseable API
)