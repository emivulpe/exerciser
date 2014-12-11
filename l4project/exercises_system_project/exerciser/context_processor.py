from exerciser.models import Application

def applications(request):
	application_list = Application.objects.all()
	for application in application_list:
		application.url = application.name.replace(' ', '_')
	return {'applications' : application_list}