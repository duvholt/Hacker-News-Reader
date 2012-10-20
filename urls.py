from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^about', 'reader.views.index', name='about'),
	url(r'^contact', 'reader.views.index', name='contact'),
	# Submission json
	url(r'^json/stories/$', 'reader.views.stories_json', name=''),
	url(r'^json/stories/(?P<page>\d+)/$', 'reader.views.stories_json', name=''),
	url(r'^json/stories/(?P<page>\d+)/(?P<limit>\d+)/$', 'reader.views.stories_json', name=''),
	# Main page submssions
	url(r'^$', 'reader.views.index', name='home'),
	url(r'^(?P<page>\d+)/$', 'reader.views.index', name=''),
	url(r'^(?P<page>\d+)/(?P<limit>\d+)/$', 'reader.views.index', name=''),

	# url(r'^comments', 'reader.views.comments', name='comments'),
	url(r'^comments/(?P<commentid>\d*)/$', 'reader.views.comments', name='comments'),
	url(r'^comments/(?P<commentid>\d*).json', 'reader.views.comments_json', name=''),

	url(r'^south_migrate/(?P<task>\w*)/$', 'reader.views.south_migrate'),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
	url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
)
urlpatterns += staticfiles_urlpatterns()
