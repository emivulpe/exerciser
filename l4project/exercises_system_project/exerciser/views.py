from django.template import RequestContext
from django.shortcuts import render_to_response
from exerciser.models import Application, Panel, Document, Change, Step, Explanation, UsageRecord, QuestionRecord, Group, Teacher, Question, Option
import json 
import simplejson 
import datetime
from django.views.decorators.csrf import requires_csrf_token
import django.conf as conf
from exerciser.forms import UserForm, GroupForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from chartit import DataPool, Chart
from django.db.models import Avg
from django.db.models import Count, Max


@requires_csrf_token
def log_info_db(request):
	print "log"
	time_on_step = request.POST['time']
	current_step = request.POST['step']
	direction = request.POST['direction']
	session_id = request.session.session_key
	application_name = request.POST['example_name']
	application = Application.objects.filter(name=application_name)[0]
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	
	record = UsageRecord(application = application, session_id = session_id, time_on_step = time_on_step, step = current_step, direction = direction, timestamp = timestamp)
	
	usergroup = request.session.get('teacher_group', None)
	print(usergroup)
	if usergroup != None:
		print "not none"
		teacher_username=usergroup[0]
		usergroup_name=usergroup[1]
		user=User.objects.filter(username=teacher_username)
		teacher=Teacher.objects.filter(user=user)
		group = Group.objects.filter(name = usergroup_name)
		if len(group)>0 and len(teacher) > 0: #both have to be >0 because we can't record only group or teacher
			print "yes"
			teacher = teacher[0]
			group = group[0]
			record.usergroup = group
			record.teacher = teacher


	record.save()
	print("test")
	return HttpResponse("{}",content_type = "application/json")

	
	
###### Similar to the other log. Refactor ############
@requires_csrf_token
def log_question_info_db(request):
	print "log question"
	time_on_question = request.POST['time']
	current_step = request.POST['step']
	session_id = request.session.session_key
	application_name = request.POST['example_name']
	answer_text = request.POST['answer']
	
	application = Application.objects.filter(name=application_name)[0]
	step = Step.objects.filter(application=application, order=current_step)[0]
	question = Question.objects.filter(step=step)[0]
	answer = Option.objects.filter(question=question,content=answer_text)[0]
	
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	usergroup= request.session.get('teacher_group', None)
	
	print(usergroup)
	question_record=QuestionRecord(application=application,question=question,answer=answer)
	if usergroup != None:
		print "not none"
		teacher_username=usergroup[0]
		usergroup_name=usergroup[1]
		user=User.objects.filter(username=teacher_username)
		teacher=Teacher.objects.filter(user=user)
		group = Group.objects.filter(name = usergroup_name)
		if len(group)>0 and len(teacher) > 0: #both have to be >0 because we can't record only group or teacher
			print "yes"
			teacher = teacher[0]
			group = group[0]
			question_record.usergroup = group
			question_record.teacher = teacher
	question_record.save()
	print("test success")
	return HttpResponse("{}",content_type = "application/json")
	
	
@requires_csrf_token
def create_group(request):
	print "in create group"
	group_name = request.POST['group']
	teacher_username = request.POST['teacher']
	user = User.objects.filter(username = teacher_username)
	teacher = Teacher.objects.filter(user=user)
	print "create"
	success = False
	if len(user)>0 and len(teacher)>0:
		user = user[0]
		teacher = teacher[0]
		print "eee", len(Group.objects.filter(teacher=teacher,name=group_name))==0
		if len(Group.objects.filter(teacher=teacher,name=group_name))==0:
			group = Group(teacher = teacher, name = group_name)
			group.save()
			success = True
			print "created"
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")

@requires_csrf_token
def register_group_with_session(request):
	print("register")
	teacher_username = request.POST['teacher']
	group_name = request.POST['group']
	success=False
	user = User.objects.filter(username=teacher_username)
	if len(user) > 0 :

		teacher = Teacher.objects.filter(user=user)
		print "teacher exists ",group_name,len(Group.objects.filter(teacher=teacher, name=group_name))
		if len(Group.objects.filter(teacher=teacher, name=group_name)) > 0:
			print "group exists"
			request.session['teacher_group'] = [teacher_username, group_name]
			success = True

	print "success",success
	return HttpResponse(simplejson.dumps(success),content_type = "application/json")

def index(request):
	# Request the context of the request.
	# The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	application_list = Application.objects.all()
	
	# Construct a dictionary to pass to the template engine as its context.
	# Note the key boldmessage is the same as {{ boldmessage }} in the template!
	context_dict = {'applications' : application_list}

	for application in application_list:
		application.url = application.name.replace(' ', '_')
	
	# Return a rendered response to send to the client.
	# We make use of the shortcut function to make our lives easier.
	# Note that the first parameter is the template we wish to use.
	return render_to_response('exerciser/index.html', context_dict, context)

def application(request, application_name_url):
	# Request our context from the request passed to us.
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
			
		"""
		explanations_str = []
		for explanation in explanations:
			explanations_str.append(str(explanation))
		"""
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

	
@login_required		
def update_teacher_interface_graph_data(request):
		# do what you need to do to get the data
		# maybe you need to pass a querystring to this view so you can work out what app to select stuff for
		app_name=request.GET['app_name']
		group_name=request.GET['group']
		
		#####
		info_type=request.GET['info_type']
		
		print "in update graph"
		print "group",group_name
		print "app",app_name

		teacher_username = request.user
		user=User.objects.filter(username=teacher_username)
		teacher=Teacher.objects.filter(user=user)
		selected_group = Group.objects.filter(name = group_name)
		selected_application=Application.objects.filter(name=app_name)
		selected_data=[]
		if len(selected_group)>0 and len(selected_application)>0 and len(teacher)>0:
			teacher = teacher[0]
			selected_group = selected_group[0]
			selected_application = selected_application[0]
			usage_records = UsageRecord.objects.filter(application=selected_application,teacher=teacher,usergroup=selected_group)
			
			if info_type=="time":
				#### Getting averages ##########
				num_steps = usage_records.aggregate(max = Max('step'))
				print "here"
				if num_steps['max'] != None:
					for step in range(1, num_steps['max']+1):
						print "in"
						records = usage_records.filter(step = step)
						average = records.aggregate(time = Avg('time_on_step'))
						selected_data.append([average['time']])
						print "hehe",step,average['time']
				################################
			else:
				question_text=request.GET['question']
				question=Question.objects.filter(application=selected_application,question_text=question_text)
				question_records = QuestionRecord.objects.filter(application=selected_application, question=question, teacher=teacher,usergroup=selected_group)
				test=question_records.values('answer').annotate(count=Count('answer')).order_by('answer')
				print test,"test"
				sv=[]
				for r in test:
					sv.append(r['count'])
				selected_data=sv
		return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")	
	

@requires_csrf_token
def teacher_interface(request):
	# Request the context of the request.
	# The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	application_list = Application.objects.all()
	
	# Construct a dictionary to pass to the template engine as its context.
	# Note the key boldmessage is the same as {{ boldmessage }} in the template!

	# for application in application_list:
	#	application.url = application.name.replace(' ', '_')
	print "fde"
	
	
	
	# If it's a HTTP POST, we're interested in processing form data.

	user_form = UserForm()
	group_form = GroupForm()
	
	context_dict = {'applications' : application_list,'user_form': user_form, 'group_form': group_form}
	
	
	# Return a rendered response to send to the client.
	# We make use of the shortcut function to make our lives easier.
	# Note that the first parameter is the template we wish to use.
	return render_to_response('exerciser/teacher_interface.html', context_dict, context)

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

    print registered
    request.session['registered'] = registered
    # Render the template depending on the context.
    return HttpResponseRedirect('/exerciser/teacher_interface')

def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    # If the request is a HTTP POST, try to pull out the relevant information.
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
                return HttpResponseRedirect('/exerciser/teacher_interface')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
		
		############# TEST THIS !!!!! #####################
        return HttpResponseRedirect('/exerciser/teacher_interface')

@login_required
def statistics(request):

	context = RequestContext(request)
	teacher_username = request.user
	print "teacher",teacher_username
	
	user = User.objects.filter(username=teacher_username)
	teacher = Teacher.objects.filter (user=user)
	groups = Group.objects.filter(teacher=teacher)
	print len(groups)
	applications = Application.objects.all();
	questions={}
	for application in applications:
		questions_text=[]
		app_questions = Question.objects.filter(application=application)
		for app_question in app_questions:
			questions_text.append(app_question.question_text)
		questions[application.name]=questions_text
	print questions
	context_dict = {'groups' : groups, 'app_questions_dict' : simplejson.dumps(questions)}
	print "YEY"
    	return render_to_response('exerciser/graph_viewer.html', context_dict, context)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/exerciser/teacher_interface')