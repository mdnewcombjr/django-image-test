from django.contrib import admin
from django.contrib.auth.views import login
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
	path('login/', login, {'template_name':'/login.html'}),
	path('', include('threadbuilder_app.urls')),
]
