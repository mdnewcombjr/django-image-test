import requests
import json
import os

from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError

from django.utils.translation import gettext, gettext_lazy as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_text, force_bytes

from formtools.wizard.views import SessionWizardView

from loomit_server import jinja2 as Jinja2Env
from loomit_server.utilities import get_client_ip
from loomit_server.storage_backends import TemporaryMediaStorage

from threadbuilder_app.tokens import account_activation_token
from threadbuilder_app.forms import SignUp
from threadbuilder_app.forms import ImageUpload
from threadbuilder_app.models import BaseImageEntry

import loomit_server.settings as settings

import logging
# GLOBAL VARS
logger = logging.getLogger("threadbuilder_app.views")


def index(request):
	template = loader.get_template('home.html')
	context = {}

	return HttpResponse(template.render(context, request))


def sign_up(request):
	template = loader.get_template('signup.html')

	if request.method == 'POST':
		form = SignUp.SignUpForm(request.POST)
		if form.is_valid():

			''' Begin reCAPTCHA validation '''
			recaptcha_response = request.POST.get('g-recaptcha-response')
			url = settings.RECAPTCHA_VERIFY_URL
			values = {
				'secret': settings.RECAPTCHA_SECRET_KEY,
				'response': recaptcha_response,
				'remoteip': get_client_ip(request)
			}
			req =  requests.post(url, data=values)
			result = req.json()
			''' End reCAPTCHA validation '''

			if result['success'] == False:
				form.add_error(None, ValidationError(_("Please complete the reCAPTCHA verification at the bottom of the page.")))
			else:
				user = form.save(commit=False)
				user.is_active = False
				user.save()
				current_site = get_current_site(request)

				email_subject = _("Activate your account")
				email_context = {
					"username": user.username,
					"domain": current_site.domain,
					"uid": str( urlsafe_base64_encode(force_bytes(user.pk)), 'utf8'),
					"token": account_activation_token.make_token(user),
				}
				message = loader.render_to_string('activation_email.html', email_context)
			
				user.email_user(email_subject, message)

				return redirect('threadbuilder_app:confirm_signup')
	else:

		form = SignUp.SignUpForm()

	context = {"form": form}

	return HttpResponse(template.render(context, request))

def confirm_signup(request):
	template = loader.get_template('generic_message.html')
	context = {
		"title": _("Thank you!"),
		"message": _("Please click on the link sent to your email address to confirm your account."),
		"next_link": reverse("threadbuilder_app:login_user"), 
	}

	return HttpResponse(template.render(context, request))

def activate(request, uidb64, token):
	template = loader.get_template("generic_message.html")

	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.profile.email_confirmed = True
		user.save()
		context = {
			"title": _("Thank you!"),
			"message": _("Your account has been activated."),
			"next_link": reverse("threadbuilder_app:login_user"),
		}
		return HttpResponse(template.render(context, request))
	else:
		return redirect('threadbuilder_app:cms_home')


#########################
#### Create Artwork #####
#########################

CREATE_ART_FORMS = [("img_upload", ImageUpload.ImageUploadForm),
					("img_crop", ImageUpload.ImageCropForm)]

class ImageUploadWizard(SessionWizardView):
	file_storage = TemporaryMediaStorage()

	CREATE_ART_TEMPLATES = {"img_upload":"create_thread_art.html",
						"img_crop":"crop_uploaded_image.html"}

	def get_template_names(self):
		return [self.CREATE_ART_TEMPLATES[self.steps.current]]

	def get_form(self, step=None, data=None, files=None):
		form = super(ImageUploadWizard, self).get_form(step, data, files)

		if step is None:
			step = self.steps.current
		
		curstep = step
		if step=="img_upload":
			pass

		if step == "img_crop":
			data = self.get_cleaned_data_for_step("img_upload")
			import pdb; pdb.set_trace()
			f = self.storage.get_step_files("img_upload")
			uploaded_img = f.get("img_upload-image", None)

			if uploaded_img is not None:
				form.fields['image'] = uploaded_img

		return form

	def done(self, form_list, form_dict, **kwargs):
		
		#Process all of the form data here

		return redirect('threadbuilder_app:upload_image_done')

def upload_image_done(request):
	template = loader.get_template('image_upload_done.html')
	context = {}
	return HttpResponse( template.render(context, request))

@login_required
def upload_image(request):
	response_data = {}

	if request.user.is_authenticated == False:
		return JsonResponse(response_data, status=403)

	if request.method == 'POST' and request.FILES['file']:
		image_entry = BaseImageEntry(image = request.FILES['file'], owner=request.user)

		form = ImageUpload.ImageUploadForm(request.POST, request.FILES, instance = image_entry)
		if form.is_valid():
			form.save()
			#response_data['image_key'] = str(image_entry.image)
			#response_data['zoom'] = str(request.POST.get('zoom', 1))
			#response_data['topleftx'] = str(request.POST.get('topleftx',0))
			#response_data['toplefty'] = str(request.POST.get('toplefty',0))
			#response_data['bottomrightx'] = str(request.POST.get('bottomrightx',0))
			#response_data['bottomrighty'] = str(request.POST.get('bottomrighty',0))

			return redirect('threadbuilder_app:upload_image_done')
		else:
			return HttpResponse(form.errors, status=400)
	elif request.method == 'GET':
		template = loader.get_template('create_thread_art.html')
		context = {}
		return HttpResponse( template.render(context, request))
	else:
		return HttpResponse(b'', status=405)