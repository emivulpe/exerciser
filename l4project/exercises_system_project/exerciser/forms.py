from exerciser.models import Teacher
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