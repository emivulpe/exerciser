from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import render_to_response
from exerciser.models import Application, Panel, Document, Change, Step, Explanation, UsageRecord, QuestionRecord, Group, Teacher, Question, Option, Student, AcademicYear, SampleQuestionnaire
import json 
import simplejson 
import datetime
import string
import random
from random import randint
from django.views.decorators.csrf import requires_csrf_token
import django.conf as conf
from exerciser.forms import UserForm, SampleQuestionnaireForm
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
	try:
		time_on_step = request.POST['time']
		current_step = int(request.POST['step'])
		direction = request.POST['direction']
		application_name = request.POST['example_name']
	except KeyError:
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	session_id = request.session.session_key

	print current_step, "CUR STER"
	print direction, "DIR"
	if direction == "back":
		current_step = int(current_step) + 1
	#### TODO add some checks if these exist ####
	try:
		application = Application.objects.filter(name=application_name)[0]
		step = Step.objects.filter(application=application, order = current_step)[0]
		print step, "STEP TEST"
	except IndexError:
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
		
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
	multiple_choice_question = request.POST['multiple_choice']
	teacher_name=request.session.get("teacher",None)

	application = Application.objects.filter(name=application_name)[0]
	step = Step.objects.filter(application=application, order=current_step)[0]
	question = Question.objects.filter(step=step)[0]
	question_record=QuestionRecord(application=application,question=question, answer_text=answer_text)
	if multiple_choice_question=="true":
		answer = Option.objects.filter(question=question,content=answer_text)[0]
		question_record.answer=answer
	


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
	

### Refactored Error handling well. Tested. Works ###
def student_group_list(request):

	context = RequestContext(request)
	try:
		group_name = request.GET['group']
		teacher_username = request.GET['teacher']
		selected_year = request.GET['year']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")

	try:
		user = User.objects.filter(username = teacher_username)[0]
		teacher = Teacher.objects.filter(user=user)[0]
		year = AcademicYear.objects.filter(start=selected_year)[0]
		group=Group.objects.filter(teacher=teacher,name=group_name,academic_year=year)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	students=Student.objects.filter(teacher=teacher,group=group)
	selected_year = selected_year +'/'+ str(int(selected_year)+1)
	return render_to_response('exerciser/groupSheet.html', {'students':students, 'group':group_name, 'year':selected_year}, context)
	

### similar to update group. Refactor. Refactored ###
@requires_csrf_token
def create_group(request):
	success = False
	try:
		teacher_username = request.POST['teacher']
		group_name = request.POST['group']
		selected_year = request.POST['year']
		num_students = request.POST['num_students']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")

	try:
		user = User.objects.filter(username = teacher_username)[0]
		teacher = Teacher.objects.filter(user=user)[0]
		year = AcademicYear.objects.filter(start=selected_year)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")

	if len(Group.objects.filter(teacher=teacher,name=group_name,academic_year=year))==0:
		group = Group(teacher = teacher, name = group_name,academic_year=year)
		group.save()
		create_student_ids(teacher,group,num_students)
		success = True

	return HttpResponse(simplejson.dumps(success),content_type = "application/json")
	
### Refactored. Checks added. Looks Fine ###
@requires_csrf_token
def delete_group(request):
	success = False
	try:
		teacher_username = request.POST['teacher']
		group_name = request.POST['group']
		selected_year = request.POST['year']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")
	
	try:
		user = User.objects.filter(username = teacher_username)[0]
		teacher = Teacher.objects.filter(user=user)[0]
		year = AcademicYear.objects.filter(start=selected_year)[0]
		group = Group.objects.filter(teacher=teacher,name=group_name,academic_year=year)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")

	group.delete()
	success = True

	return HttpResponse(simplejson.dumps(success),content_type = "application/json")


### Refactored. Checks added. Looks Fine ###
@requires_csrf_token
def update_group(request):
	success = False
	try:
		group_name = request.POST['group']
		teacher_username = request.POST['teacher']
		selected_year = request.POST['year']
		num_students = request.POST['num_students']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")
		
	try:
		user = User.objects.filter(username = teacher_username)[0]
		teacher = Teacher.objects.filter(user=user)[0]
		year = AcademicYear.objects.filter(start=selected_year)[0]
		group = Group.objects.filter(teacher=teacher,name=group_name,academic_year=year)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")

	create_student_ids(teacher,group,num_students)
	success = True
	print "created"
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")




### Refactored. Checks added. Looks Fine ###
@requires_csrf_token
def register_group_with_session(request):
	print "in reg group"
	success=False
	try:
		teacher_username = request.session['teacher']
		year = request.session['year']
		group_name = request.POST['group']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")
		
	try:
		user = User.objects.filter(username=teacher_username)[0]
		teacher = Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
		group = Group.objects.filter(teacher=teacher, academic_year = academic_year, name=group_name)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")
		
	request.session['group'] = group_name
	success = True
	print "success",success
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")

	
### Refactored. Do I really need it? ###
@requires_csrf_token
def save_session_ids(request):
	print "in save"
	request.session['registered']=True
	print "saving..."
	#return HttpResponse("{}",content_type = "application/json")
	return HttpResponseRedirect('/weave/')

### Refactored. Checks added. Looks Fine ###
@requires_csrf_token
def register_teacher_with_session(request):
	print "in reg teacher"
	success=False
	try:
		teacher_username = request.POST['teacher']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")
	try:
		user = User.objects.filter(username=teacher_username)[0]
		teacher = Teacher.objects.filter(user=user)[0]
		print "teacher exists "
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")
	request.session['teacher'] = teacher_username
	success = True
	print "success",success
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")


### Refactored ### similar to register_teacher_with_session, etc... Refactor Checks added. Looks Fine ###
@requires_csrf_token
def register_student_with_session(request):
	print "in reg student"
	success=False
	try:
		student_name = request.POST['student']
		teacher_username = request.session['teacher']
		year = request.session['year']
		group_name = request.session['group']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")

	try:
		user = User.objects.filter(username=teacher_username)[0]
		teacher = Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
		group=Group.objects.filter(teacher=teacher, academic_year = academic_year, name=group_name)[0]
		student=Student.objects.filter(teacher=teacher,group=group,student_id=student_name)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")

	print "student exists"
	request.session['student'] = student_name
	success = True
	print "success",success
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")

### Checks added. Looks Fine ###
def get_groups_for_year(request):
	try:
		year = request.POST['year']
		teacher_username = request.session['teacher']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps([]), content_type="application/json")
	try:
		user = User.objects.filter(username=teacher_username)[0]
		teacher = Teacher.objects.filter(user=user)[0]
		academic_year=AcademicYear.objects.filter(start=year)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps([]), content_type="application/json")
	groups = Group.objects.filter(teacher=teacher,academic_year = academic_year)
	print groups
	groups = map(str, groups)
	return HttpResponse(simplejson.dumps(groups), content_type="application/json")

### Refactored Checks added. Looks Fine ###
@requires_csrf_token
def register_year_with_session(request):
	success=False
	try:
		year = request.POST['year']
		teacher_username = request.session['teacher']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")

	try:
		academic_year=AcademicYear.objects.filter(start=year)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps(success), content_type="application/json")
	request.session['year'] = year
	success = True
	print "success",success
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")
	

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
	#return HttpResponse("{}",content_type = "application/json")
	
	return HttpResponseRedirect('/weave/')
	
### Refactored ###
@requires_csrf_token
def del_session_variable(request):
	try:
		to_delete=request.POST['to_delete']
	except KeyError:
		return HttpResponseRedirect('/weave/')
	print "in reset"
	if to_delete in request.session:
		del request.session[to_delete]
		print "t"
	#request.session.delete()
	#request.session.modified = True
	#return HttpResponse("{}",content_type = "application/json")
	
	return HttpResponseRedirect('/weave/')
	

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
	print "in submit questionnaire"
	
	if 'skipped' not in request.POST:
		# do what you need to do to say that a 
	
		context = RequestContext(request)

		saved = False

		# If it's a HTTP POST, we're interested in processing form data.
		if request.method == 'POST':

			questionnaire_form = SampleQuestionnaireForm(data=request.POST)

			# If the form is valid...
			if questionnaire_form.is_valid():
				# Save the user's form data to the database.
				questionnaire = questionnaire_form.save()
				teacher_username = request.user
				try:
					user=User.objects.filter(username=teacher_username)[0]
					teacher=Teacher.objects.filter(user=user)[0]
					questionnaire.teacher=teacher
				except IndexError:
					pass
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
		request.session['questionnaire_asked'] = True
		return HttpResponseRedirect('/weave/teacher_interface')
	
	# Skipped is in; this should be an AJAX call
	request.session['questionnaire_asked'] = True
	return HttpResponse('{}', content_type='application/json')


### Refactored ###
def application(request, application_name_url):
	context = RequestContext(request)
	if 'registered' in request.session:
		

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
			
			panels = Panel.objects.filter(application = application).order_by('number')
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
	else:
		return render_to_response('exerciser/index.html', {}, context)



### Checks added. Looks fine ###
def get_students(request):
	print "in get students!"
	try:
		group_name=request.GET['group']
		year = request.GET['year']
	except KeyError:
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
		
	teacher_username = request.user
	try:
		user=User.objects.filter(username=teacher_username)[0]
		teacher=Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
		selected_group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=academic_year)[0]
	except InputError:
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")

	students=Student.objects.filter(group=selected_group)
	students = map(str, students)
	return HttpResponse(simplejson.dumps(students), content_type="application/json")
	
### Checks added. Looks fine ###
def get_groups(request):
	print "in get groups!"
	try:
		year = request.GET['year']
	except KeyError:
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied in get groups'}), content_type="application/json")
	try:
		year = int(year)
	except ValueError:
		print "value error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied Value'}), content_type="application/json")
	
	teacher_username = request.user
	try:
		user=User.objects.filter(username=teacher_username)[0]
		teacher=Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
	except IndexError:
		print "Exception"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")

	groups = Group.objects.filter(teacher=teacher,academic_year=academic_year)
	groups = map(str,groups)
	return HttpResponse(simplejson.dumps(groups), content_type="application/json")
	
### Checks added. Looks fine ###
def get_steps(request):
	print "in get steps"
	try:
		app_name = request.GET['app_name']
	except KeyError:
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	
	try:
		application = Application.objects.filter(name=app_name)[0]
	except IndexError:
		print "Exception"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")

	steps = Step.objects.filter(application=application)
	steps = map(str,steps)
	return HttpResponse(simplejson.dumps(steps), content_type="application/json")
### Refactored ###
@login_required		
def get_question_data(request):
	print "in get question data"
	app_name=request.GET.get('app_name',None)
	year=request.GET.get('year',None)
	group_name=request.GET.get('group',None)
	step_num=request.GET.get('step',None)
	question_text=request.GET.get('question',None)
	student_id=request.GET.get('student',None)
	# Check for invalid request
	if (app_name is None or year is None or group_name is None) or (step_num is None and question_text is None):
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	teacher_username = request.user
	try:
		user=User.objects.filter(username=teacher_username)[0]
		teacher=Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
		group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=academic_year)[0]
		application=Application.objects.filter(name=app_name)[0]
		if question_text is not None:
			question=Question.objects.filter(application=application,question_text=question_text)[0]
		if student_id is not None:
			print student_id
			student=Student.objects.filter(teacher=teacher,group=group,student_id=student_id)[0]
		if step_num is not None:
			step=Step.objects.filter(application=application,order=step_num)[0]
			question=Question.objects.filter(application=application,step=step)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
		

	selected_data={}
	quest_text=question.question_text
	all_options=Option.objects.filter(question=question)
	question_records = QuestionRecord.objects.filter(application=application, question=question, teacher=teacher,group=group)#
	print len(question_records)
	if student_id is not None:
		print "not none"
		print len(question_records)
		question_records=question_records.filter(student=student)
	sd=[]

	for option in all_options:
		records_for_option=question_records.filter(answer=option)
		times_chosen=len(records_for_option)
		student_list=[]
		if student_id is None:
			print "student_id was none"
			for record in records_for_option:
				if record.student != None:
					stud_id=record.student.student_id
					print stud_id
					if stud_id not in student_list:
						student_list.append(stud_id)
		else:
			print "was not none"
			student_list.append(student_id)
		sd.append({option.content:times_chosen,'students':student_list})
	selected_data['question']=quest_text
	selected_data['data']=sd
	#print sd
	return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")	
def update_time_graph(request):
	"""
	If no student ID is passed, then you produce data for an group average graph.
	Otherwise, you get the total time for the student.
	"""
	app_name=request.GET.get('app_name', None)
	group_name=request.GET.get('group', None)
	year = request.GET.get('year', None)		
	student_id = request.GET.get('student', None)
	
	if app_name is None or group_name is None or year is None:
	    return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	
	teacher_username = request.user
	
	try:
		user=User.objects.filter(username=teacher_username)[0]
		teacher=Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
		selected_group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=academic_year)[0]
		selected_application=Application.objects.filter(name=app_name)[0]
		
		if student_id is not None:
			student = Student.objects.filter(student_id=student_id)[0]
	except IndexError:
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	
	print 2
	selected_data={}
	usage_records = UsageRecord.objects.filter(application=selected_application,teacher=teacher,group=selected_group)

	if student_id is not None:
		usage_records.filter(student=student)
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
				
				# If student ID is none, assume an average result, else SUM everything
				if student_id is None:
				    time = records.aggregate(time = Avg('time_on_step'))
				else:
				    time = records.aggregate(time = Sum('time_on_step'))

				revisited_steps_count=len(records.filter(direction="back"))
				print time['time'] , "Time"
				sd.append({"y":time['time'],"revisited_count":revisited_steps_count,"explanation":explanation_text,"explanation_start":explanation_text_start})
	if sd!=[]:
		selected_data["data"]=sd
		print sd , " SD PRINTED"
		selected_data["question_steps"]=question_steps

	return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")
	
### Checks added. ###
def update_class_steps_graph(request):
	print "class steps"
	try:
		app_name=request.GET['application']
		print app_name
		group_name=request.GET['group']
		print group_name
		year = request.GET['year']
		print year
		step_num=request.GET['step']
		print step_num
	except KeyError:
		print "error key"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
		
	teacher_username = request.user
	try:
		user=User.objects.filter(username=teacher_username)[0]
		teacher=Teacher.objects.filter(user=user)[0]
		academic_year = AcademicYear.objects.filter(start=year)[0]
		selected_group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=academic_year)[0]
		application=Application.objects.filter(name=app_name)[0]
		step = Step.objects.filter(application=application, order = step_num)[0]
	except IndexError:
		print "error index"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	selected_data={}
	sd=[]
	usage_records = UsageRecord.objects.filter(application=application,teacher=teacher,group=selected_group,step=step)

	for record in usage_records:
		if record.student != None:
			sd.append({record.student.student_id:record.time_on_step})
	selected_data["data"]=sd
	print selected_data, "SELECTED DATA!!!!"

	return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")


### Refactored Checks added Looks ok ###
def populate_summary_table(request):
	try:
		application=request.GET['application']
		academic_year=request.GET['year']
		group_name=request.GET['group']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	teacher_username = request.user
	try:
		user=User.objects.filter(username=teacher_username)[0]
		teacher=Teacher.objects.filter(user=user)[0]
		year=AcademicYear.objects.filter(start=academic_year)[0]
		selected_application=Application.objects.filter(name=application)
		total_steps=selected_application.aggregate(num_steps=Count('step'))['num_steps']
		selected_application = selected_application[0]
		group = Group.objects.filter(name = group_name,teacher=teacher,academic_year=year)[0]

	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	selected_data={}

	students=Student.objects.filter(teacher=teacher,group=group)

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
	return HttpResponse(simplejson.dumps({"selected_data":selected_data,"total_steps":total_steps}), content_type="application/json")	

def get_application_questions(request):
	try:
		application = request.GET['application']
	except KeyError:
		print "error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	try:
		selected_application = Application.objects.filter(name=application)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	questions = Question.objects.filter(application=application)
	questions = map(str, questions)
	print questions, "questions"
	return HttpResponse(simplejson.dumps(questions), content_type="application/json")

### Refactored. Ask if I have to check if request was get/post ###
@requires_csrf_token
def teacher_interface(request):
	# Request the context of the request.
	# The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	application_list = Application.objects.all()
	academic_years = AcademicYear.objects.all()

	user_form = UserForm()
	#group_form = GroupForm()

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

	questionnaire_form = SampleQuestionnaireForm()

	context_dict = {'applications' : application_list,'user_form': user_form, 'groups': groups,'academic_years':academic_years,'questionnaire_form':questionnaire_form}
	
	
	# Return a rendered response to send to the client.
	# We make use of the shortcut function to make our lives easier.
	# Note that the first parameter is the template we wish to use.
	return render_to_response('exerciser/teacher_interface.html', context_dict, context)

#def questionnaire_asked(request):

### Refactored. Ask if I have to check if request was get/post ###
def register(request):
	print "in register"
	# Like before, get the request's context.
	context = RequestContext(request)

	# A boolean value for telling the template whether the registration was successful.
	# Set to False initially. Code changes value to True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		print "was post"
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
		user_form = UserForm(data=request.POST)
		#group_form = GroupForm(data=request.POST)

		# If the form is valid...
		if user_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()
			teacher=Teacher(user=user)
			try:
				can_analyse=bool(request.POST['can_analyse'])
				teacher.can_analyse=can_analyse
				print "can ",can_analyse,request.POST['can_analyse']
			except KeyError:
				print "KeyERROR"
				pass
			except ValueError:
				print "VALUE ERROR"
				pass
			teacher.save()
			print teacher,"teacher"

			# Update our variable to tell the template registration was successful.
			registered = True

		# Invalid form - mistakes or something else?
		# Print problems to the terminal.
		# They'll also be shown to the user.
		else:
			print user_form.errors #, group_form.errors

	print registered,"registered"
	request.session['registered'] = registered
	# Render the template depending on the context.
	return HttpResponseRedirect('/weave/teacher_interface')
	

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
            return HttpResponseRedirect('/weave/teacher_interface')

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
				try:
					teacher=Teacher.objects.filter(user=user)[0]
					questionnaire=SampleQuestionnaire.objects.filter(teacher=teacher)
					if len(questionnaire)>0:
						request.session['questionnaire_asked'] = True
				except IndexError:
					pass
					

	request.session['successful_login'] = successful_login
	return HttpResponseRedirect('/weave/teacher_interface')

### Refactored ###
@login_required
def statistics(request):

	context = RequestContext(request)
	teacher_username = request.user
	try:
		user = User.objects.filter(username=teacher_username)[0]
		teacher = Teacher.objects.filter (user=user)[0]
	except IndexError:
		print "error"
		return HttpResponse(simplejson.dumps({'error':'Bad input supplied'}), content_type="application/json")
	applications = Application.objects.all();
	academic_years=AcademicYear.objects.all()
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


	context_dict = {'application_names' : application_names, 'app_questions_dict' : simplejson.dumps(questions), 'academic_years': academic_years}
	return render_to_response('exerciser/graph_viewer.html', context_dict, context)

# Use the login_required() decorator to ensure only those logged in can access the view.

### Looks OK ###
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/weave/teacher_interface')