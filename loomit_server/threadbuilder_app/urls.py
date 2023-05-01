from django.urls import path, re_path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from threadbuilder_app.forms import ImageUpload



app_name = 'threadbuilder_app'
urlpatterns = [
    path('', views.index, name='cms_home'),
	path('signup', views.sign_up, name='sign_up'),
	path('signup/confirm', views.confirm_signup, name='confirm_signup'),
	re_path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

	path('login', LoginView.as_view(template_name="user_login.html"), name='login_user'),
	path('logout', LogoutView.as_view(), name='logout_user'),

	path('create', views.upload_image, name='create_artwork'),
	path('create-finished',views.upload_image_done, name='upload_image_done'),
]