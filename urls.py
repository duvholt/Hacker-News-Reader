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
	# url(r'^about', 'reader.views.index'),
	(r'about$', TemplateView.as_view(template_name='about.html')),
	# url(r'^contact', 'reader.views.index'),
	url(r'^command/(?P<command>\w+)/$', 'reader.views.command', name='command'),
	# Main page submssions
	url(r'^$', 'reader.views.index', name='index'),
	url(r'^(?P<story_type>news|newest|best|active|ask)$', 'reader.views.index', name='index_type'),
	# Main page json
	url(r'^.json$', 'reader.views.index', {'json': True}, name='index_json'),
	url(r'^(?P<story_type>news|newest|best|active|ask).json$', 'reader.views.index', {'json': True}, name='index_type_json'),
	# Comments
	url(r'^comments/(?P<commentid>\d*)/$', 'reader.views.comments', name='comments'),
	url(r'^comments/(?P<commentid>\d*).json', 'reader.views.comments', {'json': True}, name='comments_json'),
	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
	# Just a simple redirect for the favicon
	url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
	url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
)
# Couldn't find a decent way to serve staticfiles with AppFog
if settings.DEBUG:
	urlpatterns += staticfiles_urlpatterns()
else:
	urlpatterns += patterns('',
		(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
	)
