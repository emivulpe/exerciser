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
		doc_id = docAttrDict['ID']
		doc = add_document(doc_id,docAttrDict)
		for fragment in document:
			fragAttrDict = fragment.attrib
			add_fragment(doc,fragAttrDict)

	# Print out what we have added to the user.
	for d in Document.objects.all():
		for f in Fragment.objects.filter(document = d):
			print "- {0} - {1}".format(str(d), str(f))



def add_document(document_id,attributesDict):
	type = attributesDict['type']
	kind = attributesDict['kind']
	try:
		document_type=DocumentType.objects.filter(name=type, kind=kind)[0]
	except IndexError:
		print "document type doesn't exist"
		return None
	document_name = attributesDict['name']

	fixOrder = json.loads(attributesDict['FixOrder'])
	d = Document.objects.get_or_create(id = document_id, name = document_name, document_type = document_type, fixOrder = fixOrder)[0]
	return d

# ASK how to populate style depending on fragment type automatically
def add_fragment(doc, attributesDict):
	type = attributesDict['type']
	document_type=doc.document_type
	try:
		fragment_type=FragmentType.objects.filter(name=type,document_type=document_type)[0]
		fragment_style=FragmentStyle.objects.filter(type=fragment_type)[0]
	except IndexError:
		print "Fragment type doesn't exist"
		return None
	id = attributesDict['ID']
	text = attributesDict['value']
	text = text.replace(' ','&nbsp')
	if text.endswith(';'):
		text = text[:text.rfind(";"):] + "<br/>"

	order = json.loads(attributesDict['order'])
	f = Fragment.objects.get_or_create(document = doc,id = id, text = text, style = fragment_style, type = fragment_type, order = order)[0]
	return f

# Start execution here!
if __name__ == '__main__':
	print "Starting DocumentFragment population script..."
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exercises_system_project.settings')
	from exerciser.models import Document, Fragment, FragmentType, DocumentType, FragmentStyle
	populate("C:\Users\Emi\Desktop\lvl4project\project\Current IWE\Resources\projects\cs1ct\Documents.xml")