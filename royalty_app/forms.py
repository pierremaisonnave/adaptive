from django.forms import ModelForm


from .models import *

class CustomerForm(ModelForm):
	class Meta:
		model = User_profile_picture
		fields = '__all__'
		exclude = ['user']