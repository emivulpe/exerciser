import os
import xml.etree.ElementTree as ET
import json


def populate(filepath):

    file = open(filepath,'r')
    tree = ET.parse(file)
    root = tree.getroot()
    for application in root:
        add_application(application)


    # Print out what we have added to the user.
    for a in Application.objects.all():
        for p in Panel.objects.filter(application = a):
            print "- {0} - {1}".format(str(a), str(p))



def add_application(element):
	applicationAttributesDict = element.attrib
	name = applicationAttributesDict['name']
	layout = applicationAttributesDict['layout']
	a = Application.objects.get_or_create(name = name, layout = layout)[0]
	for panel in element.iter('panel'):
		panelAttributesDict = panel.attrib
		add_panel(a,panelAttributesDict)
	return a
	
def add_panel(application, attributesDict):
	print(attributesDict)
	number = json.loads(attributesDict['number'])
	type = attributesDict['type']
	documentName = attributesDict['content']
	document = Document.objects.get(name = documentName)
	p = Panel.objects.get_or_create(application = application, number = number, type = type, document = document)[0]
	return p

# Start execution here!
if __name__ == '__main__':
    print "Starting DocumentFragment population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exercises_system_project.settings')
    from exerciser.models import Document, Application, Panel
    populate("C:\Users\Emi\Desktop\lvl4project\project\Current IWE\Resources\projects\cs1ct\Applications.xml")