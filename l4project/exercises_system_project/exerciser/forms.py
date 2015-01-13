from exerciser.models import Teacher, SampleQuestionnaire
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'password')
		
	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)

		for fieldname in ['username']:
			self.fields[fieldname].help_text = None
		
class GroupForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('can_analyse',)
		
		
class SampleQuestionnaireForm(forms.ModelForm):
	"""
	your_name = forms.CharField(label='Your name', max_length=100)
	cc_myself = forms.BooleanField(required=False)
	CHOICES=[('select1','select 1'),('select2','select 2')]
	like = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())
	"""
	class Meta:
		model = SampleQuestionnaire
		fields = ('school','bool','comment','year_in_school','year_in_school2')
		
 		widgets = {
            'year_in_school2': forms.RadioSelect(attrs={'class': 'myfieldclass'}),
        }
