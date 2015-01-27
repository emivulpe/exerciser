from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import render_to_response
from exerciser.models import Application, Panel, Document, Change, Step, Explanation, UsageRecord, QuestionRecord, Group, Teacher, Question, Option, Student, AcademicYear
import json 
import simplejson 
import datetime
import string
import random
from random import randint
from django.views.decorators.csrf import requires_csrf_token
import django.conf as conf
from exerciser.forms import UserForm, GroupForm, SampleQuestionnaireForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from chartit import DataPool, Chart
from django.db.models import Avg
from django.db.models import Count, Max, Sum


### Refactored ###
def create_student_ids(teacher,group,number_students_needed):
	created=0
	ids=[]
	while (created < int(number_students_needed)):
		id=random.choice(string.lowercase)
		id+=str(randint(10, 99))
		students=Student.objects.filter(teacher=teacher,group=group,student_id=id)
		if len(students)==0:
			student=Student(teacher=teacher,group=group,student_id=id)
			student.save()
			ids.append(id)
			created += 1
	print ids,"IDS"


### Refactored + TODO ###
@requires_csrf_token
def log_info_db(request):

	time_on_step = request.POST['time']
	current_step = int(request.POST['step'])
	direction = request.POST['direction']
	print direction, "DIR"
	if direction == "back":
		current_step = int(current_step) + 1
	session_id = request.session.session_key
	application_name = request.POST['example_name']
	print current_step, "CUR STER"
	#### TODO add some checks if these exist ####
	application = Application.objects.filter(name=application_name)[0]
	step = Step.objects.filter(application=application, order = current_step)[0]
	print step, "STEP TEST"

	


	record = UsageRecord(application = application, session_id = session_id, time_on_step = time_on_step, step = step, direction = direction)
	
	teacher_name=request.session.get("teacher",None)

	if teacher_name != None:
	
		user=User.objects.filter(username=teacher_name)
		teacher=Teacher.objects.filter(user=user)
		
		#### TODO maybe remove these checks. It is impossible that they don't exist.... ####
		if len(teacher)>0:
			teacher=teacher[0]
			record.teacher = teacher
			group_name=request.session.get("group",None)
			year = request.session.get("year",None)
			if group_name != None and year != None:
				academic_year = AcademicYear.objects.filter(start = year)[0]
				print academic_year, "AY TEST"
				group = Group.objects.filter(teacher=teacher, academic_year = academic_year, name = group_name)
				if len(group) > 0:
					group=group[0]
					record.group = group
					student_name=request.session.get("student", None)
					if student_name != None:
						student = Student.objects.filter(teacher=teacher,group=group,student_id=student_name)
						if len(student) > 0:
							student=student[0]
							record.student = student

	record.save()
	return HttpResponse("{}",content_type = "application/json")

	
	
###### Similar to the other log. Refactor. Refactored + TODO ############
@requires_csrf_token
def log_question_info_db(request):

	time_on_question = request.POST['time']
	current_step = request.POST['step']
	session_id = request.session.session_key
	application_name = request.POST['example_name']
	answer_text = request.POST['answer']
	teacher_name=request.session.get("teacher",None)

	application = Application.objects.filter(name=application_name)[0]
	step = Step.objects.filter(application=application, order=current_step)[0]
	question = Question.objects.filter(step=step)[0]
	answer = Option.objects.filter(question=question,content=answer_text)[0]
	
	question_record=QuestionRecord(application=application,question=question,answer=answer)

	if teacher_name != None:
		user=User.objects.filter(username=teacher_name)
		teacher=Teacher.objects.filter(user=user)
		if len(teacher)>0:
			teacher=teacher[0]
			question_record.teacher = teacher
			year=request.session.get("year",None)
			group_name=request.session.get("group",None)
			if group_name != None and year != None:
				academic_year = AcademicYear.objects.filter(start=year)[0]
				group = Group.objects.filter(teacher=teacher, academic_year = academic_year, name = group_name)
				if len(group) > 0:
					group=group[0]
					question_record.group = group
					
					student_name=request.session.get("student", None)
					if student_name != None:
						student = Student.objects.filter(teacher=teacher,group=group,student_id=student_name)
						if len(student) > 0:
							student=student[0]
							question_record.student = student

	question_record.save()
	print("test success")
	return HttpResponse("{}",content_type = "application/json")
	

### Refactored ###
def student_group_list(request):

	context = RequestContext(request)
	group_name = request.GET.get('group', None)
	teacher_username = request.GET.get('teacher', None)
	selected_year = request.GET.get('year', None)
	
	user = User.objects.filter(username = teacher_username)
	teacher = Teacher.objects.filter(user=user)[0]
	year = AcademicYear.objects.filter(start=selected_year)[0]
	group=Group.objects.filter(teacher=teacher,name=group_name,academic_year=year)[0]
	students=Student.objects.filter(teacher=teacher,group=group)
	selected_year = selected_year +'/'+ str(int(selected_year)+1)
	return render_to_response('exerciser/groupSheet.html', {'students':students, 'group':group_name, 'year':selected_year}, context)
	

### similar to update group. Refactor. Refactored ###
@requires_csrf_token
def create_group(request):

	teacher_username = request.POST['teacher']
	group_name = request.POST['group']
	selected_year = request.POST['year']

	num_students = request.POST['num_students']

	user = User.objects.filter(username = teacher_username)
	teacher = Teacher.objects.filter(user=user)
	year = AcademicYear.objects.filter(start=selected_year)[0]

	success = False
	if len(user)>0 and len(teacher)>0:
		user = user[0]
		teacher = teacher[0]

		if len(Group.objects.filter(teacher=teacher,name=group_name,academic_year=year))==0:
			group = Group(teacher = teacher, name = group_name,academic_year=year)
			group.save()
			create_student_ids(teacher,group,num_students)
			success = True

	return HttpResponse(simplejson.dumps(success),content_type = "application/json")

@requires_csrf_token
def delete_group(request):

	teacher_username = request.POST['teacher']
	group_name = request.POST['group']
	selected_year = request.POST['year']

	user = User.objects.filter(username = teacher_username)
	teacher = Teacher.objects.filter(user=user)
	year = AcademicYear.objects.filter(start=selected_year)[0]

	success = False
	if len(user)>0 and len(teacher)>0:
		user = user[0]
		teacher = teacher[0]

		if len(Group.objects.filter(teacher=teacher,name=group_name,academic_year=year))>0:
			group = Group.objects.filter(teacher = teacher, name = group_name,academic_year=year)
			group.delete()
			success = True

	return HttpResponse(simplejson.dumps(success),content_type = "application/json")
	

### Refactored ###
@requires_csrf_token
def update_group(request):

	group_name = request.POST['group']
	teacher_username = request.POST['teacher']
	selected_year = request.POST['year']
	num_students = request.POST['num_students']

	user = User.objects.filter(username = teacher_username)
	teacher = Teacher.objects.filter(user=user)
	year = AcademicYear.objects.filter(start=selected_year)[0]

	success = False
	if len(user)>0 and len(teacher)>0:
		user = user[0]
		teacher = teacher[0]

		if len(Group.objects.filter(teacher=teacher,name=group_name,academic_year=year))>0:
			group = Group.objects.filter(teacher=teacher,name=group_name,academic_year=year)[0]
			create_student_ids(teacher,group,num_students)
			success = True
			print "created"
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")




### Refactored ###
@requires_csrf_token
def register_group_with_session(request):

	teacher_username = request.session['teacher']
	year = request.session['year']
	group_name = request.POST['group']

	success=False
	user = User.objects.filter(username=teacher_username)
	if len(user) > 0 :
		teacher = Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
		if len(Group.objects.filter(teacher=teacher, academic_year = academic_year, name=group_name)) > 0:
			request.session['group'] = group_name
			success = True
	print "success",success
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")

	
### Refactored. Do I really need it? ###
@requires_csrf_token
def save_session_ids(request):
	request.session['registered']=True
	print "saving..."
	return HttpResponse("{}",content_type = "application/json")

### Refactored ###
@requires_csrf_token
def register_teacher_with_session(request):
	teacher_username = request.POST['teacher']

	success=False
	user = User.objects.filter(username=teacher_username)

	if len(user) > 0 :
		teacher = Teacher.objects.filter(user=user)
		print "teacher exists "

		request.session['teacher'] = teacher_username
		success = True
	print "success",success
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")


### Refactored ### similar to register_teacher_with_session, etc... Refactor ###
@requires_csrf_token
def register_student_with_session(request):

	student_name = request.POST['student']
	
	teacher_username = request.session['teacher']
	year = request.session['year']
	group_name = request.session['group']
	
	success=False
	user = User.objects.filter(username=teacher_username)
	if len(user)>0:
		user=user[0]
		teacher = Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
		group=Group.objects.filter(teacher=teacher, academic_year = academic_year, name=group_name)[0]
		student=Student.objects.filter(teacher=teacher,group=group,student_id=student_name)
		if len(student) > 0:
			print "student exists"
			request.session['student'] = student_name
			success = True
		print "success",success
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")


### Refactored ###
@requires_csrf_token
def register_year_with_session(request):

	year = request.POST['year']
	teacher_username = request.session['teacher']
	user = User.objects.filter(username=teacher_username)

	success=False

	academic_years=AcademicYear.objects.filter(start=year)

	if len(academic_years) > 0 and len(user)>0:
		teacher = Teacher.objects.filter(user=user)[0]
		academic_year = academic_years[0]
		print "teacher exists "
		groups = Group.objects.filter(teacher=teacher,academic_year = academic_year)
		
		group_names=[]
		for group in groups:
			group_names.append(group.name)
			
		request.session['year'] = year
		success = True
	print "success",success
	return HttpResponse(simplejson.dumps({"success":success,"groups":group_names}),content_type = "application/json")
	

### Refactored ###
@requires_csrf_token
def reset_session(request):
	
	print "in reset"
	if 'teacher' in request.session:
		del request.session['teacher']
		print "t"
	if 'year' in request.session:
		del request.session['year']
		print "y"
	if 'group' in request.session:
		del request.session['group']
		print "g"
	if 'student' in request.session:
		del request.session['student']
		print "s"
	if 'registered' in request.session:
		del request.session['registered']
		print "r"
	
	request.session.delete()
	request.session.modified = True
	return HttpResponse("{}",content_type = "application/json")
	

### Refactored ###
def index(request):
	# Request the context of the request.
	# The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	application_list = Application.objects.all()
	academic_years = AcademicYear.objects.all()
	
	# Construct a dictionary to pass to the template engine as its context.
	# Note the key boldmessage is the same as {{ boldmessage }} in the template!
	context_dict = {'applications' : application_list, 'academic_years':academic_years}

	for application in application_list:
		application.url = application.name.replace(' ', '_')
	
	# Return a rendered response to send to the client.
	# We make use of the shortcut function to make our lives easier.
	# Note that the first parameter is the template we wish to use.
	return render_to_response('exerciser/index.html', context_dict, context)


### Refactored ###
@requires_csrf_token
def submit_questionnaire(request):

	context = RequestContext(request)

	saved = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':

		questionnaire_form = SampleQuestionnaireForm(data=request.POST)

		# If the form is valid...
		if questionnaire_form.is_valid():
			# Save the user's form data to the database.
			questionnaire = questionnaire_form.save()
			questionnaire.save()
			saved = True

		# Invalid form - mistakes or something else?
		# Print problems to the terminal.
		# They'll also be shown to the user.
		else:
			print questionnaire_form.errors
	else:
		form = SampleQuestionnaireForm()

	print saved,"form saved"
	return HttpResponseRedirect('/exerciser/teacher_interface')


### Refactored ###
def application(request, application_name_url):

	context = RequestContext(request)

	# Change underscores in the category name to spaces.
	# URLs don't handle spaces well, so we encode them as underscores.
	# We can then simply replace the underscores with spaces again to get the name.
	application_name = application_name_url.replace('_', ' ')

	# Create a context dictionary which we can pass to the template rendering engine.
	# We start by containing the name of the category passed by the user.
	context_dict = {'application_name': application_name}
	
	

	try:

		application = Application.objects.get(name=application_name)
		context_dict['application'] = application
		
		panels = Panel.objects.filter(application = application)
		context_dict['panels'] = panels

		steps = Step.objects.filter(application=application)
		stepChanges = []
		explanations = []
		for step in steps:
			changesToAdd = []
			changes = Change.objects.filter(step = step)
			for change in changes:
				changesFound = change.getChanges()
				for c in changesFound:
					changesToAdd.append(c)
			stepChanges.append(changesToAdd)
			expl = Explanation.objects.filter(step = step)
			for explanation in expl:
				explanations.append(json.dumps((explanation.text).replace('"',"&quot")))
			

		context_dict['steps'] = json.dumps(stepChanges)
		context_dict['explanations'] = explanations
		size_panels = (100/len(panels))
		context_dict['panel_size'] = str(size_panels)
	except Application.DoesNotExist:
		# We get here if we didn't find the specified category.
		# Don't do anything - the template displays the "no category" message for us.
		pass

	# Go render the response and return it to the client.
	return render_to_response('exerciser/application.html', context_dict, context)

	
	
def update_graph_answers(request):
		app_name=request.GET['app_name']
		group_name=request.GET['group']
		year = request.GET['year']		
		question_text=request.GET['question']
		
		teacher_username = request.user
		user=User.objects.filter(username=teacher_username)
		teacher=Teacher.objects.filter(user=user)
		academic_year = AcademicYear.objects.filter(start=year)[0]
		selected_group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=academic_year)
		selected_application=Application.objects.filter(name=app_name)

		selected_data=[]
		if len(selected_group)>0 and len(selected_application)>0 and len(teacher)>0:

			teacher = teacher[0]
			selected_group = selected_group[0]
			selected_application = selected_application[0]


			question=Question.objects.filter(application=selected_application,question_text=question_text)[0]
			all_options=Option.objects.filter(question=question)

			question_records = QuestionRecord.objects.filter(application=selected_application, question=question, teacher=teacher,group=selected_group)

			for option in all_options:
				records_for_option=question_records.filter(answer=option)
				times_chosen=len(records_for_option)
				student_list=[]
				for record in records_for_option:
					if record.student != None:
						student_id=record.student.student_id
						print student_id
						if student_id not in student_list:
							student_list.append(student_id)
				selected_data.append({option.content:times_chosen,'students':student_list})
		return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")	
	
def update_graph_time(request):
		app_name=request.GET['app_name']
		group_name=request.GET['group']
		year = request.GET['year']		
		print 1
		teacher_username = request.user
		user=User.objects.filter(username=teacher_username)
		teacher=Teacher.objects.filter(user=user)
		academic_year = AcademicYear.objects.filter(start=year)[0]
		selected_group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=academic_year)
		selected_application=Application.objects.filter(name=app_name)
		print 2
		selected_data={}
		if len(selected_group)>0 and len(selected_application)>0 and len(teacher)>0:
			print 3
			teacher = teacher[0]
			selected_group = selected_group[0]
			selected_application = selected_application[0]
			usage_records = UsageRecord.objects.filter(application=selected_application,teacher=teacher,group=selected_group)
			print 4
			question_steps=[]
			app_questions=Question.objects.filter(application=selected_application)
			for question in app_questions:
				question_steps.append(question.step.order)
			print 5
			sd=[]
			#### Getting averages ##########
			steps = Step.objects.filter(application=selected_application)
			num_steps = steps.aggregate(max = Max('order'))
			print 6
			if num_steps['max'] != None:
				print 7
				print num_steps['max'], "step num"
				for step_num in range(1, num_steps['max']+1):
					print step_num, " step num"
					explanation_text=""
					step=steps.filter(order=step_num)
					if len(step)>0:
						step=step[0]
						explanation=Explanation.objects.filter(step=step)
						if len(explanation)>0:
							explanation=explanation[0]
							explanation_text=explanation.text
							if len(explanation_text)<100:
								explanation_text_start=explanation_text[:len(explanation_text)]
							else:
								explanation_text_start=explanation_text[:100]

						records = usage_records.filter(step = step)
						average = records.aggregate(time = Avg('time_on_step'))

						revisited_steps_count=len(records.filter(direction="back"))
						print average['time'] , "AVG"
						sd.append({"y":average['time'],"revisited_count":revisited_steps_count,"explanation":explanation_text,"explanation_start":explanation_text_start})
			if sd!=[]:
				selected_data["data"]=sd
				print sd , " SD PRINTED"
				selected_data["question_steps"]=question_steps

		return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")

		
def update_graph_class_steps(request):
		print "ERHAEHREAGHEARGHE"
		app_name=request.GET['app_name']
		group_name=request.GET['group']
		year = request.GET['year']		

		teacher_username = request.user
		user=User.objects.filter(username=teacher_username)
		teacher=Teacher.objects.filter(user=user)
		academic_year = AcademicYear.objects.filter(start=year)[0]
		selected_group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=academic_year)
		selected_application=Application.objects.filter(name=app_name)

		selected_data=[]
		if len(selected_group)>0 and len(selected_application)>0 and len(teacher)>0:

			teacher = teacher[0]
			selected_group = selected_group[0]
			selected_application = selected_application[0]
			usage_records = UsageRecord.objects.filter(application=selected_application,teacher=teacher,group=selected_group)

			usage_records=usage_records.filter(step=1) #######   HARDCODED   CHANGE   #############

			for record in usage_records:
				selected_data.append({record.student.student_id:record.time_on_step})
		print selected_data, "SELECTED DATA!!!!"

		return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")	


### Refactored. Refactor. Hardcode ###
@login_required		
def update_teacher_interface_graph_data(request):

		app_name=request.GET['app_name']
		group_name=request.GET['group']
		year = request.GET['year']		
		
		info_type=request.GET['info_type']

		teacher_username = request.user
		user=User.objects.filter(username=teacher_username)
		teacher=Teacher.objects.filter(user=user)
		academic_year = AcademicYear.objects.filter(start=year)[0]
		selected_group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=academic_year)
		selected_application=Application.objects.filter(name=app_name)

		selected_data={}
		if len(selected_group)>0 and len(selected_application)>0 and len(teacher)>0:

			teacher = teacher[0]
			selected_group = selected_group[0]
			selected_application = selected_application[0]
			usage_records = UsageRecord.objects.filter(application=selected_application,teacher=teacher,group=selected_group)
			question_steps=[]
			app_questions=Question.objects.filter(application=selected_application)
			for question in app_questions:
				question_steps.append(question.step.order)
			
			sd=[]
			if info_type=="time":

				#### Getting averages ##########
				num_steps = usage_records.aggregate(max = Max('step'))

				if num_steps['max'] != None:
					for step_num in range(1, num_steps['max']+1):
						explanation_text=""
						step=Step.objects.filter(application=selected_application,order=step_num)
						if len(step)>0:
							step=step[0]
							explanation=Explanation.objects.filter(step=step)
							if len(explanation)>0:
								explanation=explanation[0]
								explanation_text=explanation.text
								if len(explanation_text)<100:
									explanation_text_start=explanation_text[:len(explanation_text)]
								else:
									explanation_text_start=explanation_text[:100]
					
						records = usage_records.filter(step = step_num)
						average = records.aggregate(time = Avg('time_on_step'))
						
						revisited_steps_count=len(records.filter(direction="back"))

						sd.append({"y":average['time'],"revisited_count":revisited_steps_count,"explanation":explanation_text,"explanation_start":explanation_text_start})

				print sd,"SD"
				################################
			elif info_type=="answers":
				print "answers"
				question_text=request.GET['question']
				question=Question.objects.filter(application=selected_application,question_text=question_text)[0]
				all_options=Option.objects.filter(question=question)
				
				question_records = QuestionRecord.objects.filter(application=selected_application, question=question, teacher=teacher,group=selected_group)

				for option in all_options:
					records_for_option=question_records.filter(answer=option)
					times_chosen=len(records_for_option)
					student_list=[]
					for record in records_for_option:
						student_id=record.student.student_id
						print student_id
						if student_id not in student_list:
							student_list.append(student_id)
					sd.append({option.content:times_chosen,'students':student_list})
			else:
				print "!!!!!!!!!!!!!!!!!!!else"
				usage_records=usage_records.filter(step=1) #######   HARDCODED   CHANGE   #############
				#print usage_records 
				
				for record in usage_records:
					sd.append({record.student.student_id:record.time_on_step})
				print sd, "SDDDDDDDDDDDDDDDDDDDDDDDDDDD"
			if sd!=[]:
				selected_data["data"]=sd
				selected_data["question_steps"]=question_steps
		return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")	


### Refactored ###
def get_step_data(request):

	application=request.GET['application']
	year=request.GET['year']
	group_name=request.GET['group']
	step_num=request.GET['step']
	teacher_username = request.user

	user=User.objects.filter(username=teacher_username)
	teacher=Teacher.objects.filter(user=user)
	academic_year = AcademicYear.objects.filter(start=year)[0]

	selected_application=Application.objects.filter(name=application)

	selected_data=[]
	if len(teacher) > 0:
		teacher = teacher[0]
		selected_group = Group.objects.filter(name = group_name,teacher=teacher,academic_year = academic_year)
		if len(selected_group) > 0:
			selected_group = selected_group[0]
			if len(selected_application) > 0:
				selected_application = selected_application[0]
				step = Step.objects.filter(application=application, order = step_num)
				if len(step) > 0:
					step = step[0]
					usage_records = UsageRecord.objects.filter(application=selected_application,teacher=teacher,group=selected_group,step=step)

					for record in usage_records:
						if record.student != None:
							selected_data.append({record.student.student_id:record.time_on_step})
	print selected_data, "SELECTED DATA"
		
	return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")	


### Refactored ###
def populate_summary_table(request):

	application=request.GET['application']
	academic_year=request.GET['year']
	group_name=request.GET['group']
	teacher_username = request.user
	
	user=User.objects.filter(username=teacher_username)
	if len(user) > 0:
		teacher=Teacher.objects.filter(user=user)[0]
	
		year=AcademicYear.objects.filter(start=academic_year)[0]
	
		group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=year)
		if len(group) > 0:
			group = group[0]
			students=Student.objects.filter(teacher=teacher,group=group)
	
			selected_data={}

			selected_application=Application.objects.filter(name=application)
			if len(selected_application) > 0:

				total_steps=selected_application.aggregate(num_steps=Count('step'))
				selected_application = selected_application[0]

				for student in students:

					student_id=student.student_id

					student_records=UsageRecord.objects.filter(application=selected_application,teacher=teacher,group=group,student=student)
					
					last_step_reached=student_records.aggregate(last_step=Max('step'))
					
					if last_step_reached['last_step'] == None:
						last_step_reached = 0
					else:
						last_step_reached = last_step_reached['last_step']
						
					total_app_time=student_records.aggregate(time_on_step=Sum('time_on_step'))
					
					if total_app_time['time_on_step'] == None:
						total_app_time = 0
					else: 
						total_app_time = total_app_time['time_on_step']
						
					revisited_steps_count=student_records.filter(direction='back').aggregate(count_revisits=Count('id'))['count_revisits']
					print student_id, last_step_reached,total_app_time,revisited_steps_count
					
					selected_data[student_id]={'last_step':last_step_reached,'total_time':total_app_time,'num_steps_revisited':revisited_steps_count}
	print selected_data
	return HttpResponse(simplejson.dumps({"selected_data":selected_data,"total_steps":total_steps['num_steps']}), content_type="application/json")	
	
	
### Refactored ###
@login_required		
def get_question_data(request):

		app_name=request.GET['app_name']
		year=request.GET['year']
		group_name=request.GET['group']
		step_num=request.GET['step']
		teacher_username = request.user
		
		# get teacher
		user=User.objects.filter(username=teacher_username)

		if len(user) > 0:
			teacher=Teacher.objects.filter(user=user)[0]
			academic_year=AcademicYear.objects.filter(start=year)[0]
			#get group
			group = Group.objects.filter(teacher = teacher, name = group_name,academic_year=academic_year)
			
			#get application
			application=Application.objects.filter(name=app_name)

			#get step
			step=Step.objects.filter(application=application,order=step_num)

			selected_data={}
			question_text=""
			if len(group)>0 and len(application)>0 and len(step)>0:
				group = group[0]
				application = application[0]
				step=step[0]

				question=Question.objects.filter(application=application,step=step)
				if len(question)>0:
					question=question[0]
					question_text=question.question_text
					all_options=Option.objects.filter(question=question)
					question_records = QuestionRecord.objects.filter(application=application, question=question, teacher=teacher,group=group)
					answers=question_records.values('answer').annotate(count=Count('answer')).order_by('answer')
					
					sd=[]

					for option in all_options:
						records_for_option=question_records.filter(answer=option)
						times_chosen=len(records_for_option)
						student_list=[]
						for record in records_for_option:
							if record.student != None:
								student_id=record.student.student_id
								print student_id
								if student_id not in student_list:
									student_list.append(student_id)
						sd.append({option.content:times_chosen,'students':student_list})
					selected_data['question']=question_text
					selected_data['data']=sd
					print sd
		return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")	

	
### Refactored. Ask if I have to check if request was get/post ###
@requires_csrf_token
def teacher_interface(request):
	# Request the context of the request.
	# The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	application_list = Application.objects.all()
	academic_years = AcademicYear.objects.all()

	user_form = UserForm()
	group_form = GroupForm()

	groups={}

	if request.user.is_authenticated():

		teacher_username = request.user
		user = User.objects.filter(username=teacher_username)
		teacher = Teacher.objects.filter (user=user)
		for academic_year in academic_years:
			group_objects = Group.objects.filter(teacher=teacher, academic_year=academic_year)
			group_names=[]
			for group in group_objects:
				group_names.append(str(group.name))
			groups[academic_year.start]= group_names


	context_dict = {'applications' : application_list,'user_form': user_form, 'group_form': group_form,'groups': groups,'academic_years':academic_years}
	
	
	# Return a rendered response to send to the client.
	# We make use of the shortcut function to make our lives easier.
	# Note that the first parameter is the template we wish to use.
	return render_to_response('exerciser/teacher_interface.html', context_dict, context)


### Refactored. Ask if I have to check if request was get/post ###
def register(request):

    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        group_form = GroupForm(data=request.POST)

        # If the form is valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            
            # Now sort out the GroupProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            group = group_form.save(commit=False)
            group.user = user

            # Now we save the UserProfile model instance.
            group.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, group_form.errors

    print registered,"registered"
    request.session['registered'] = registered
    # Render the template depending on the context.
    return HttpResponseRedirect('/exerciser/teacher_interface')
	

### Looks OK ###
def questionnaire(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SampleQuestionnaireForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/exerciser/teacher_interface')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SampleQuestionnaireForm()

    return render(request, 'exerciser/questionnaire.html', {'form': form})
	
	
### Looks OK ###
def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    # If the request is a HTTP POST, try to pull out the relevant information.
    successful_login = False

    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                successful_login = True


    request.session['successful_login'] = successful_login
    return HttpResponseRedirect('/exerciser/teacher_interface')

### Refactored ###
@login_required
def statistics(request):

	context = RequestContext(request)
	teacher_username = request.user
	
	user = User.objects.filter(username=teacher_username)
	teacher = Teacher.objects.filter (user=user)

	applications = Application.objects.all();
	application_names=[]
	questions={}
	for application in applications:
		application_names.append(str(application.name))
		
		app_questions = Question.objects.filter(application=application)
		if len(app_questions)>0:
			questions_text=[]
			for app_question in app_questions:
				questions_text.append(app_question.question_text)
			questions[application.name]=questions_text

	academic_years=AcademicYear.objects.all()
	groups={}
	for academic_year in academic_years:
			group_objects = Group.objects.filter(teacher=teacher, academic_year=academic_year)
			group_names=[]
			for group in group_objects:
				group_names.append(str(group.name))
			groups[academic_year.start]= group_names
	context_dict = {'application_names' : application_names, 'groups' : groups, 'app_questions_dict' : simplejson.dumps(questions), 'academic_years': academic_years}
	print groups, "GROUPS"
	return render_to_response('exerciser/graph_viewer.html', context_dict, context)

# Use the login_required() decorator to ensure only those logged in can access the view.

### Looks OK ###
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/exerciser/teacher_interface')