import os
import xml.etree.ElementTree as ET
import json


def populate(filepath):

    file = open(filepath,'r')
    tree = ET.parse(file)
    root = tree.getroot()
    for document in root:
        docAttrDict = document.attrib
        docName = docAttrDict['name']
        doc = add_document(docAttrDict)
        for fragment in document:
            fragAttrDict = fragment.attrib
            add_fragment(doc,fragAttrDict)

    # Print out what we have added to the user.
    for d in Document.objects.all():
        for f in Fragment.objects.filter(document = d):
            print "- {0} - {1}".format(str(d), str(f))



def add_document(attributesDict):
	name = attributesDict['name']
	type = attributesDict['type']
	kind = attributesDict['kind']
	fixOrder = json.loads(attributesDict['FixOrder'])
	d = Document.objects.get_or_create(name = name, type = type, kind = kind, fixOrder = fixOrder)[0]
	return d
	
def add_fragment(doc, attributesDict):
	id = attributesDict['ID']
	text = attributesDict['value']
	text = text.strip()
	if text.endswith(';'):
		text = text[:text.rfind(";"):] + "<br/>"
	
	#text = original_text[:original_text.rfind(";"):]
	type = attributesDict['type']
	order = json.loads(attributesDict['order'])
	f = Fragment.objects.get_or_create(document = doc,id = id, text = text, type = type, order = order)[0]
	return f

# Start execution here!
if __name__ == '__main__':
    print "Starting DocumentFragment population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exercises_system_project.settings')
    from exerciser.models import Document, Fragment
    populate("C:\Users\Emi\Desktop\lvl4project\project\Current IWE\Resources\projects\cs1ct\Documents.xml")