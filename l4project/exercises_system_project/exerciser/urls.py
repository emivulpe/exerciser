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
		url(r'^register_year_with_session', views.register_year_with_session, name='register_year_with_session'),
		url(r'^teacher_interface/', views.teacher_interface, name='teacher_interface'),
		url(r'^update_graph/$', views.update_teacher_interface_graph_data, name='update_graph'),
		url(r'^update_graph_time/$', views.update_graph_time, name='update_graph_time'),
		url(r'^update_graph_answers/$', views.update_graph_answers, name='update_graph_answers'),
		url(r'^update_graph_class_steps/$', views.update_graph_class_steps, name='update_graph_class_steps'),
		url(r'^update_graph_student/$', views.update_graph_student, name='update_graph_student'),
		url(r'^question_graph/$', views.get_question_data, name='get_question_data'),
		url(r'^register/$', views.register, name='register'),
		url(r'^login/$', views.user_login, name='login'),
		url(r'^statistics/', views.statistics, name='statistics'),
		url(r'^create_group/', views.create_group, name='create_group'),
		url(r'^update_group/', views.update_group, name='update_group'),
		url(r'^delete_group/', views.delete_group, name='delete_group'),
		url(r'^logout/$', views.user_logout, name='logout'),
		url(r'^save_session_ids/', views.save_session_ids, name='save_session_ids'),
		url(r'^questionnaire/', views.questionnaire, name='questionnaire'),
		url(r'^submit_questionnaire/', views.submit_questionnaire, name='submit_questionnaire'),
		url(r'^reset_session', views.reset_session, name='reset_session'),
		url(r'^get_group_list', views.student_group_list, name='student_group_list'),
		url(r'^populate_summary_table', views.populate_summary_table, name='populate_summary_table'),
		url(r'^get_step_data', views.get_step_data, name='get_step_data'),
		url(r'^get_students', views.get_students, name='get_students'),
		url(r'^get_groups', views.get_groups, name='get_groups'),
		) 