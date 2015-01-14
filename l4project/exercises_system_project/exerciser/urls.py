from django.conf.urls import patterns, url
from exerciser import views

urlpatterns = patterns('',
		url(r'^$', views.index, name='index'),
		url(r'^application/(?P<application_name_url>\w+)/$', views.application, name='application'),
		url(r'^log_info_db', views.log_info_db, name='log_info_db'),
		url(r'^log_question_info_db', views.log_question_info_db, name='log_question_info_db'),
		url(r'^register_group_with_session', views.register_group_with_session, name='register_group_with_session'),
		url(r'^register_teacher_with_session', views.register_teacher_with_session, name='register_teacher_with_session'),
		url(r'^register_student_with_session', views.register_student_with_session, name='register_student_with_session'),
		url(r'^teacher_interface/', views.teacher_interface, name='teacher_interface'),
		url(r'^update_graph', views.update_teacher_interface_graph_data, name='update_graph'),
		url(r'^question_graph', views.get_question_data, name='get_question_data'),
		url(r'^register/$', views.register, name='register'),
		url(r'^login/$', views.user_login, name='login'),
		url(r'^statistics/', views.statistics, name='statistics'),
		url(r'^create_group/', views.create_group, name='create_group'),
		url(r'^update_group/', views.update_group, name='update_group'),
		url(r'^create_student/', views.create_student, name='create_student'),
		url(r'^logout/$', views.user_logout, name='logout'),
		url(r'^save_session_ids/', views.save_session_ids, name='save_session_ids'),
		url(r'^questionnaire/', views.questionnaire, name='questionnaire'),
		url(r'^submit_questionnaire/', views.submit_questionnaire, name='submit_questionnaire'),
		url(r'^reset_session', views.reset_session, name='reset_session'),
		url(r'^get_group_list', views.student_group_list, name='student_group_list'),
		) 