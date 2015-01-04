import os
import xml.etree.ElementTree as ET
import json


def populate(filepath):

	file = open(filepath,'r')
	tree = ET.parse(file)
	root = tree.getroot()
	for process in root:
		processAttrDict = process.attrib
		application = get_application(processAttrDict)
		for step in process:
			stepAttrDict = step.attrib
			s = add_step(application, stepAttrDict)
			for element in step: 
				if element.tag == 'change':
					add_change(application,s,element)
				elif element.tag == 'explanation':
					add_explanation(s,element)



    # Print out what we have added to the user.
	
	

def get_application(attributesDict):
	app_name = attributesDict['app']
	application = Application.objects.get(name = app_name)
	return application
	
def add_step(application, attributesDict):
    order = attributesDict['num']
    s = Step.objects.get_or_create(application=application, order = order)[0]
    return s

#assumes that fragment and operation appear at most once. If more, the last value is taken
def add_change(application, step, element):
	fragment = None
	operation = ''
	document = ''
	
	
	for child in element:
		#print(child.tag)
		for child in element:
			if child.tag == 'fragname':
				fragmentId = child.attrib['id']
				#print('fragment', fragmentId)
				fragment = Fragment.objects.get(id = fragmentId)
			elif child.tag == 'operation':
				operation = child.text
				#print(operation)
			elif child.tag == 'docname':
				documentName = child.text
				document = Document.objects.get(name = documentName)
			elif child.tag == 'question':
				question_text = child.attrib['content']
				question = Question.objects.get_or_create(application=application, step = step, question_text = question_text)[0]
				for option in child:
					optionAttributesList = option.attrib
					number = json.loads(optionAttributesList['num'])
					content = optionAttributesList['content']
					o = Option.objects.get_or_create(question = question, number = number, content = content)[0]
			else: 
				print(child.tag)
		if operation != 'Ask Answer':
			c = Change.objects.get_or_create(document = document, step = step, fragment = fragment, operation = operation)[0]
		else:
			c = Change.objects.get_or_create(document = document, step = step, question = question, operation = operation)[0]
			
def add_explanation(step, element):
	text = element.text
	text = text.replace('\n','<br>').replace('\r', '<br>');
	e = Explanation.objects.get_or_create(step = step, text = text)[0]
	return e
"""	
def add_question(step, question):
	questionAttributesDict = question.attrib
	question_text = questionAttributesDict['content']
	questionType = questionAttributesDict['type']
	q = Question.objects.get_or_create(step = step, question_text = question_text)[0]
	if questionType == 'MULTI_CHOICE':
		for option in question:
			optionAttributesList = option.attrib
			number = json.loads(optionAttributesList['num'])
			content = optionAttributesList['content']
			o = Option.objects.get_or_create(question = q, number = number, content = content)[0]
	return q
"""
# Start execution here!
if __name__ == '__main__':
    print "Starting DocumentFragment population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exercises_system_project.settings')
    from exerciser.models import Step, Change, Question, Explanation, Option, Fragment, Document, Application
    populate("C:\Users\Emi\Desktop\lvl4project\project\Current IWE\Resources\projects\cs1ct\Processes.xml")