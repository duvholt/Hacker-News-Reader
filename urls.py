from django.conf.urls import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from reader.views import *
import settings

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
	# Voting
	url(r'^vote/(?P<id>\d+)/$', VoteView.as_view(), name='vote'),
	url(r'^vote/(?P<id>\d+).json$', VoteJsonView.as_view(), name='vote'),
	# User page
	url(r'^user/(?P<username>\w+)/$', UserView.as_view(), name='userpage'),
	url(r'^user/(?P<username>\w+)\.json$', UserJsonView.as_view(), name='userpage_json'),
	# User login
	url(r'^login$', LoginView.as_view(), name='login'),
	url(r'^logout', LogoutView.as_view(), name='logout'),
	# Just a simple redirect for the favicon
	url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
	url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
)

if settings.DEBUG:
	urlpatterns += staticfiles_urlpatterns()
