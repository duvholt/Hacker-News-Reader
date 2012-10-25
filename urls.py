from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

story_types = '(?P<story_type>news|newest|best|active|ask)'

urlpatterns = patterns('',
	url(r'^about', 'reader.views.index'),
	url(r'^contact', 'reader.views.index'),
	url(r'^migrate/$', 'reader.views.migrate'),
	# Main page submssions
	# I hope there is a better way to do this
	url(r'^$', 'reader.views.index'),
	url(r'^page/(?P<page>\d+)(/limit/(?P<limit>\d+))?/$', 'reader.views.index'),
	url(r'^limit/(?P<limit>\d+)(/page/(?P<page>\d+))?/$', 'reader.views.index'),

	url(r'^limit/(?P<limit>\d+)/over/(?P<over>\d+)(/page/(?P<page>\d+))?/$', 'reader.views.index'),
	url(r'^limit/(?P<limit>\d+)(/page/(?P<page>\d+))?/over/(?P<over>\d+)/$', 'reader.views.index'),
	url(r'^page/(?P<page>\d+)/over/(?P<over>\d+)(/limit/(?P<limit>\d+))?/$', 'reader.views.index'),
	url(r'^page/(?P<page>\d+)(/limit/(?P<limit>\d+))?/over/(?P<over>\d+)/$', 'reader.views.index'),
	
	url(r'^' + story_types + '/$', 'reader.views.index'),
	url(r'^' + story_types + '/page/(?P<page>\d+)(/limit/(?P<limit>\d+))?/$', 'reader.views.index'),
	url(r'^' + story_types + '/limit/(?P<limit>\d+)(/page/(?P<page>\d+))?/$', 'reader.views.index'),

	url(r'^over/(?P<over>\d+)/$', 'reader.views.index'),
	url(r'^over/(?P<over>\d+)/page/(?P<page>\d+)(/limit/(?P<limit>\d+))?/$', 'reader.views.index'),
	url(r'^over/(?P<over>\d+)/limit/(?P<limit>\d+)(/page/(?P<page>\d+))?/$', 'reader.views.index'),
	# Ugh, so messy
	url(r'^' + story_types + '/over/(?P<over>\d+)/$', 'reader.views.index'),
	url(r'^' + story_types + '/over/(?P<over>\d+)/page/(?P<page>\d+)(/limit/(?P<limit>\d+))?/$', 'reader.views.index'),
	url(r'^' + story_types + '/over/(?P<over>\d+)/limit/(?P<limit>\d+)(/page/(?P<page>\d+))?/$', 'reader.views.index'),
	url(r'^' + story_types + '/limit/(?P<limit>\d+)/over/(?P<over>\d+)(/page/(?P<page>\d+))?/$', 'reader.views.index'),
	url(r'^' + story_types + '/page/(?P<page>\d+)/over/(?P<over>\d+)(/limit/(?P<limit>\d+))?/$', 'reader.views.index'),
	url(r'^' + story_types + '/limit/(?P<limit>\d+)(/page/(?P<page>\d+))?/over/(?P<over>\d+)/$', 'reader.views.index'),
	url(r'^' + story_types + '/page/(?P<page>\d+)(/limit/(?P<limit>\d+))?/over/(?P<over>\d+)/$', 'reader.views.index'),
	# Comments
	url(r'^comments/(?P<commentid>\d*)/$', 'reader.views.comments'),
	url(r'^comments/(?P<commentid>\d*).json', 'reader.views.comments_json'),
	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
	# Just a simple redirect for the favicon
	url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
)
urlpatterns += staticfiles_urlpatterns()
