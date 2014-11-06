from django import template
from exerciser.models import Fragment

register = template.Library()

@register.filter(name='lookup')
def cut(value, arg):
    return value[arg]
	
@register.filter(name='getFragmentText')
def getFragmentText(fragment_id):
    return Fragment.objects.get(id = fragment_id).text
	