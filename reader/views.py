from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.core import serializers
import json
import reader.cache as cache
from reader.models import HNComments, Stories


def index(request, page=1, limit=20):
	limit = int(limit)
	page = int(page)
	context_instance = RequestContext(request)
	cache.update_stories(0)
	stories = cache.stories(page, limit)
	pages = stories.paginator.page_range
	visible_pages = 6
	if stories.paginator.num_pages > visible_pages:
		diff = visible_pages / 2
		if page > diff:
			left = page - diff
			right = page + diff
			if stories.paginator.num_pages - page < diff:
				left = left - (diff - (stories.paginator.num_pages - page))
		else:
			left = 0
			right = visible_pages
		pages = pages[left:right]
	return render_to_response("templates/index.html", {"stories": stories, "pages": pages, 'limit': limit}, context_instance)


def stories_json(request, page=1, limit=20):
	cache.update_stories()
	stories = cache.stories(page, limit)
	return HttpResponse(serializers.serialize("json", stories), mimetype='application/json')


def comments_json(request, commentid):
	cache.update_comments(commentid)
	comments = cache.comments(commentid)
	return HttpResponse(serializers.serialize("json", comments), mimetype='application/json')


def comments(request, commentid):
	context_instance = RequestContext(request)
	cache.update_comments(commentid)
	comments = cache.comments(commentid)
	story = Stories.objects.get(pk=commentid)
	return render_to_response('templates/comments.html', {'comments': comments, 'story': story}, context_instance)
