from exerciser.models import Teacher, SampleQuestionnaire
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput())
	password2 = forms.CharField(widget=forms.PasswordInput())
	username.label = "Username:"
	password.label = "Password:"
	password2.label = "Confirm password:"
	
	print dir(password2)

	class Meta:
		model = User
		fields = ('username', 'password')
		
	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)

		for fieldname in ['username']:
			self.fields[fieldname].help_text = None
	def clean(self):
		password1 = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('password2')

		if password1 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")

		return self.cleaned_data
"""		
class GroupForm(forms.ModelForm):
    class Meta:
        model = Teacher
        
"""
		
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
