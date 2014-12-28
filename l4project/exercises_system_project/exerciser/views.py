from django.template import RequestContext
from django.shortcuts import render_to_response
from exerciser.models import Application, Panel, Process, Document, Change, Step, Explanation, UsageRecords, QuestionsData, Group
import json 
import simplejson 
import logging
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


logger = logging.getLogger(__name__)



@requires_csrf_token
def log_info_db(request):
	time_on_step = request.POST['time']
	current_step = request.POST['step']
	direction = request.POST['direction']
	session_id = request.session.session_key
	example_name = request.POST['example_name']
	application = Application.objects.filter(name=example_name)[0]
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	usergroup_name = request.session.get('group', None)
	print(usergroup_name)
	if usergroup_name != None:
		user = User.objects.filter(username = usergroup_name)
		record = UsageRecords(application = application, usergroup = user[0], session_id = session_id, time_on_step = time_on_step, step = current_step, direction = direction, timestamp = timestamp)
	else:
		record = UsageRecords(application = application, session_id = session_id, time_on_step = time_on_step, step = current_step, direction = direction, timestamp = timestamp)
	record.save()
	print("test")
	return HttpResponse("{}",content_type = "application/json")
	
	


@requires_csrf_token
def log_info(request):
	print("test3")
	time = request.POST['time']
	current_step = request.POST['step']
	direction = request.POST['direction']
	answer = request.POST['answer']
	filename ="C://Users//Emi//" +  request.session.session_key + ".txt"
	logging.basicConfig(filename=filename,level=logging.INFO)
	logger.info("Time: " + time + " " + "[" + direction + "] Going to step " + current_step + answer)
	return HttpResponse("{}",content_type = "application/json")
	
@requires_csrf_token
def register_group_with_session(request):
	print("register")
	group = request.POST['group']
	request.session['group'] = group
	return HttpResponse("{}",content_type = "application/json")

	
	
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
			
		process = Process.objects.filter(application = application)
		
		steps = Step.objects.filter(process = process)
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


def update_teacher_interface_graph_data(request):
		# do what you need to do to get the data
		# maybe you need to pass a querystring to this view so you can work out what app to select stuff for
		app_name=request.GET['app_name']
		selected_application=Application.objects.filter(name=app_name)[0]
		selected_data_source = UsageRecords.objects.filter(application=selected_application)
		selected_data=[]
		for record in selected_data_source:
			print "update"
			selected_data.append([record.step,record.time_on_step])
		return HttpResponse(simplejson.dumps(selected_data), content_type="application/json")	
	
	
	
@requires_csrf_token	
def teacher_interface(request):
	# Request the context of the request.
	# The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	application_list = Application.objects.all()
	
	# Construct a dictionary to pass to the template engine as its context.
	# Note the key boldmessage is the same as {{ boldmessage }} in the template!
	context_dict = {'applications' : application_list}

	# for application in application_list:
	#	application.url = application.name.replace(' ', '_')
	print "fde"
	if request.POST.get('application'):
		selected_application_name= request.POST['application']
		selected_application=Application.objects.filter(name=selected_application_name)[0]
	else:
		selected_application = application_list[0]
	selected_data_source =  UsageRecords.objects.filter(application=selected_application)
	selected_data=[]
	for record in selected_data_source:
		print "update"
		selected_data.append([record.step,record.time_on_step])
	
	print selected_data
	
	#Step 1: Create a DataPool with the data we want to retrieve.
	data = \
		DataPool(
		series=
			[{'options': {
			'source': selected_data_source},
			'terms': [
				'step',
				'time_on_step',]}
			])
	#Step 2: Create the Chart object
	cht = Chart(
			datasource = data,
			series_options =
			  [{'options':{
				'type': 'line',
				'stacking': False},
				'terms':{
				'step': [
					'time_on_step',]
				}}],
			chart_options =
			  {'title': {
				'text': selected_application.name},
			'xAxis': {
					'title': {
					'text': 'Step number'}}})
	
	context_dict['some_chart'] = cht
	print selected_application,"YEY"
	
	context_dict['test_data'] = [129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4, 29.9, 71.5, 106.4]
	context_dict['data'] = selected_data
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

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        group_form = GroupForm()

    # Render the template depending on the context.
    return render_to_response(
            'exerciser/register.html',
            {'user_form': user_form, 'group_form': group_form,'registered': registered},
            context)	


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
        return render_to_response('exerciser/login.html', {}, context)
		
@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")
	
	
# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/exerciser/teacher_interface')