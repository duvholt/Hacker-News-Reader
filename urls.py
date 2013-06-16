from django.conf.urls.defaults import *
# from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
import settings
from reader.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns(
	'',
	# About page
	(r'about$', TemplateView.as_view(template_name='about.html')),
	# Main page submssions
	url(r'^$', IndexView.as_view(), name='index'),
	url(r'^(?P<story_type>news|newest|best|active|self|poll|show|ask)$', IndexView.as_view(), name='index_type'),
	# Main page json
	url(r'^\.json$', IndexJsonView.as_view(), name='index_json'),
	url(r'^(?P<story_type>news|newest|best|active|self|poll|show|ask)\.json$', IndexJsonView.as_view(), name='index_type_json'),
	# Comments
	url(r'^comments/(?P<commentid>\d+)/$', CommentsView.as_view(), name='comments'),
	url(r'^comments/(?P<commentid>\d+)\.json$', CommentsJsonView.as_view(), name='comments_json'),
	# User page
	url(r'^user/(?P<username>\w+)/$', UserView.as_view(), name='userpage'),
	url(r'^user/(?P<username>\w+)\.json$', UserJsonView.as_view(), name='userpage_json'),
	# Just a simple redirect for the favicon
	url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
	url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
)
if settings.DEBUG:
	urlpatterns += staticfiles_urlpatterns()
