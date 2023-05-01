from __future__ import absolute_import  # Python 2 only

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import translation

from jinja2 import Environment

def add_css(widget, css_str):
	return widget.as_widget(attrs={"class":css_str})

def add_attributes(widget, *args):
	new_attrs = {}
	pos = 0
	while pos < (len(args)-1):
		new_attrs[args[pos]] = args[pos+1]
		pos += 2

	return widget.as_widget(attrs = new_attrs)

def environment(**options):
	env = Environment(extensions=['jinja2.ext.i18n'],**options)
	env.globals.update({
		'static': staticfiles_storage.url,
		'url': reverse,
	})

	env.filters['add_css'] = add_css
	env.filters['add_attributes'] = add_attributes

	env.install_gettext_translations(translation)
	return env