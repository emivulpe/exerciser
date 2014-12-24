from exerciser.models import Group
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'password')
		
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('can_analyse',)