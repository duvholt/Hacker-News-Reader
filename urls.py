from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
	# url(r'^about', 'reader.views.index'),
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
	url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
	url(r'^robots\.txt$', 'django.views.generic.simple.redirect_to', {'url': '/static/robots.txt'}),
)
urlpatterns += patterns('django.views.generic.simple',
	(r'about$', 'direct_to_template', {'template': 'about.html'}),
)
# Couldn't find a decent way to serve staticfiles with AppFog
if settings.DEBUG:
	urlpatterns += staticfiles_urlpatterns()
else:
	urlpatterns += patterns('',
		(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
	)
