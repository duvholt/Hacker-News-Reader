from django.conf.urls.defaults import *
# from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns(
	'',
	# About page
	(r'about$', TemplateView.as_view(template_name='about.html')),
	# This was really only used for AppFog due to lack of proper command execution.
	#url(r'^command/(?P<command>\w+)/$', 'reader.views.command', name='command'),
	# Main page submssions
	url(r'^$', 'reader.views.index', name='index'),
	url(r'^(?P<story_type>news|newest|best|active|self|poll|show|ask)$', 'reader.views.index', name='index_type'),
	# Main page json
	url(r'^\.json$', 'reader.views.index', {'json': True}, name='index_json'),
	url(r'^(?P<story_type>news|newest|best|active|self|poll|show|ask)\.json$', 'reader.views.index', {'json': True}, name='index_type_json'),
	# Comments
	url(r'^comments/(?P<commentid>\d+)/$', 'reader.views.comments', name='comments'),
	url(r'^comments/(?P<commentid>\d+)\.json$', 'reader.views.comments', {'json': True}, name='comments_json'),
	# User page
	url(r'^user/(?P<username>\w+)/$', 'reader.views.userpage', name='userpage'),
	url(r'^user/(?P<username>\w+)\.json$', 'reader.views.userpage', {'json': True}, name='userpage_json'),
	# User login
	url(r'^login$', 'reader.views.login', name='login'),
	url(r'^logout', 'reader.views.logout', name='logout'),
	# Just a simple redirect for the favicon
	url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
	url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
)
if settings.DEBUG:
	urlpatterns += staticfiles_urlpatterns()
