from django.template import RequestContext
from django.shortcuts import render_to_response
from exerciser.models import Application, Panel, Process, Document, Change, Step, Explanation
import json 
import logging
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
import django.conf as conf


logger = logging.getLogger(__name__)

def myfunction():
    logger.debug("this is a debug message!")
 
def myotherfunction():
    logger.error("this is an error message!!")
	
@requires_csrf_token
def log_info(request):
	time = request.POST['time']
	current_step = request.POST['step']
	direction = request.POST['direction']
	answer = request.POST['answer']
	filename ="C://Users//Emi//" +  request.session.session_key + ".txt"
	logging.basicConfig(filename=filename,level=logging.INFO)
	logger.info("Time: " + time + " " + "[" + direction + "] Going to step " + current_step + answer)
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
	
def teacher_interface(request):
	# Request the context of the request.
	# The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	# application_list = Application.objects.all()
	
	# Construct a dictionary to pass to the template engine as its context.
	# Note the key boldmessage is the same as {{ boldmessage }} in the template!
	# context_dict = {'applications' : application_list}

	# for application in application_list:
	#	application.url = application.name.replace(' ', '_')
	
	# Return a rendered response to send to the client.
	# We make use of the shortcut function to make our lives easier.
	# Note that the first parameter is the template we wish to use.
	return render_to_response('exerciser/teacher_interface.html', {}, context)

	