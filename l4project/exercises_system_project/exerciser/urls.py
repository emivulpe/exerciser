from django.conf.urls import patterns, url
from exerciser import views

urlpatterns = patterns('',
		url(r'^$', views.index, name='index'),
		url(r'^application/(?P<application_name_url>\w+)/$', views.application, name='application'),
		url(r'^log_info_db', views.log_info_db, name='log_info_db'),
		url(r'^register_group_with_session', views.register_group_with_session, name='register_group_with_session'),
		url(r'^log_info', views.log_info, name='log_info'),
		url(r'^teacher_interface/', views.teacher_interface, name='teacher_interface'),
		url(r'^update_graph', views.update_teacher_interface_graph_data, name='update_graph'),
		url(r'^register/$', views.register, name='register'),
		url(r'^login/$', views.user_login, name='login'),
		url(r'^statistics/', views.statistics, name='statistics'),
		url(r'^add_group/', views.add_group, name='add_group'),
		url(r'^create_group/', views.create_group, name='create_group'),
		url(r'^logout/$', views.user_logout, name='logout'),
		) 