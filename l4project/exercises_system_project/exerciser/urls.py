from django.conf.urls import patterns, url
from exerciser import views

urlpatterns = patterns('',
		url(r'^$', views.index, name='index'),
		url(r'^application/(?P<application_name_url>\w+)/$', views.application, name='application'),
		url(r'^log_info_db', views.log_info_db, name='log_info_db'),
		url(r'^log_info', views.log_info, name='log_info'),
		url(r'^teacher_interface/', views.teacher_interface, name='teacher_interface'),
		url(r'^register/$', views.register, name='register'),
		url(r'^login/$', views.user_login, name='login'),
		url(r'^restricted/', views.restricted, name='restricted'),
		url(r'^logout/$', views.user_logout, name='logout'),
		) 