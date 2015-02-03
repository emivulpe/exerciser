import os
import xml.etree.ElementTree as ET
import json


def populate(filepath):

	file = open(filepath,'r')
	tree = ET.parse(file)
	root = tree.getroot()
	for document_type in root:
		document_type_attr_dict=document_type.attrib
		document_id = document_type_attr_dict['ID']
		document_type_name = document_type_attr_dict['name']
		add_document_type(document_type_attr_dict)
		for fragment_type in document_type:
			fragment_type_attr_dict=fragment_type.attrib
			fragment_type_name = fragment_type_attr_dict['name']
			add_fragment_type(document_type_name,fragment_type_attr_dict)
			for text_style in fragment_type:
				text_style_attr_dict = text_style.attrib
				add_fragment_style(document_type_name,fragment_type_name,text_style_attr_dict)
"""
	# Print out what we have added to the user.
	for d in Document.objects.all():
		for f in Fragment.objects.filter(document = d):
			print "- {0} - {1}".format(str(d), str(f))
"""



	
def add_fragment_style(document_type_name,fragment_type_name, text_style_attr_dict):
	try:
		document_type=DocumentType.objects.filter(name=document_type_name)[0]
		fragment_type=FragmentType.objects.filter(document_type=document_type,name=fragment_type_name)[0]
	except IndexError:
		print "Document or fragment type doesn't exist"
		return None
	font = text_style_attr_dict['font']
	font_size = text_style_attr_dict['size']
	str_to_bool(text_style_attr_dict['bold'])
	bold = str_to_bool(text_style_attr_dict['bold'])
	italic = str_to_bool(text_style_attr_dict['italic'])
	underlined = str_to_bool(text_style_attr_dict['underline'])

	fragmet_style = FragmentStyle.objects.get_or_create(font = font,bold = bold, italic = italic, underlined = underlined, font_size = font_size,type=fragment_type)[0]
	return fragmet_style
	
def add_document_type(document_type_attr_dict):

	name = document_type_attr_dict['name']
	kind = document_type_attr_dict['kind']

	document_type = DocumentType.objects.get_or_create(name=name,kind=kind)[0]
	return document_type
	
def add_fragment_type(document_type_name,fragment_type_attr_dict):
	try:
		document_type=DocumentType.objects.filter(name=document_type_name)[0]
	except IndexError:
		print "Document doesn't exist"
		return None
	name = fragment_type_attr_dict['name']
	kind = fragment_type_attr_dict['kind']

	fragment_type = FragmentType.objects.get_or_create(document_type=document_type,name=name,kind=kind)[0]
	return document_type
	

def str_to_bool(s):
	if s == 'true':
		 return True
	elif s == 'false':
		 return False
	else:
		 raise ValueError
# Start execution here!
if __name__ == '__main__':
	print "Starting DocumentFragment population script..."
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exercises_system_project.settings')
	from exerciser.models import FragmentStyle, Document, DocumentType, FragmentType
	populate("C:\Users\Emi\Desktop\lvl4project\project\Current IWE\Resources\projects\cs1ct\Doc Types.xml")