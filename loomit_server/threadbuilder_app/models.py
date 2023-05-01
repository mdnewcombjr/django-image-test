from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver

from loomit_server.storage_backends import MediaStorage

import uuid

UPLOADED_IMAGE_STORAGE = MediaStorage()

class TimeStampedModel(models.Model):
	created_on = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)
	class Meta:
		abstract = True

class PublishableModel(TimeStampedModel):
	published_on = models.DateTimeField(blank = True, editable=False, null = True)
	class Meta:
		abstract = True

######################################################
#################### PROFILE MODELS ##################
######################################################

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	email_confirmed = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	try:
		profile = instance.profile
	except Profile.DoesNotExist:
		Profile.objects.create(user=instance)

	instance.profile.save()

######################################################
#################### USER CONTENT MODELS #############
######################################################

def img_upload_to(instance, filename):
	return 'user_{0}/{1}'.format(instance.owner.id, str(uuid.uuid4()) )

class BaseImageEntry(models.Model):
	''' 
		This model represents an entry in a job queue of an image to be converted into thread art
	'''
	owner = models.ForeignKey(User, on_delete = models.CASCADE)
	image = models.ImageField(storage=MediaStorage(), upload_to=img_upload_to)
	zoom = models.FloatField()
	top_left_x = models.IntegerField()
	top_left_y = models.IntegerField()
	bottom_right_x = models.IntegerField()
	bottom_right_y = models.IntegerField()

	processing_complete = models.BooleanField(default=False)
	processing_started = models.BooleanField(default=False)

