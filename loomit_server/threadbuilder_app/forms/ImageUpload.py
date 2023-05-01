from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from threadbuilder_app.models import BaseImageEntry

class ImageUploadForm(ModelForm):
	class Meta:
		model = BaseImageEntry
		fields = ['image','top_left_x', 'top_left_y', 'bottom_right_x', 'bottom_right_y', 'zoom']

class ImageCropForm(forms.Form):
	image = forms.ImageField()
	topLeftX = forms.IntegerField()
	topLeftY = forms.IntegerField()
	bottomRightX = forms.IntegerField()
	bottomRightY = forms.IntegerField()