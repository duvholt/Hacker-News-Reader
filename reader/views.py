from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.core import serializers
import reader.cache as cache
from reader.models import Stories, HNComments, Poll
from django.core import management


def index(request, story_type='news'):
	limit = request.GET.get('limit', None)
	page = request.GET.get('page', 1)
	over = request.GET.get('over', None)
	if not limit:
		limit_cookie = request.COOKIES.get('stories_limit')
		if limit_cookie:
			limit = int(limit_cookie)
		else:
			limit = 25
	else:
		try:
			limit = int(limit, 10)
		except ValueError:
			limit = 25
	if over:
		try:
			over = int(over, 10)
			# story_type = 'over'
		except ValueError:
			over = None
	try:
		page = int(page)
	except ValueError:
		page = 1
	context_instance = RequestContext(request)
	cache.update_stories(story_type=story_type, over_filter=over)
	stories = cache.stories(page, limit, story_type=story_type, over_filter=over)
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
	response = render_to_response("templates/index.html", {"stories": stories, "pages": pages, 'limit': limit}, context_instance)
	response.set_cookie('stories_limit', limit)
	return response


def stories_json(request, page=1, limit=25):
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
	story = None
	polls = None
	total_votes = 0
	try:
		story = Stories.objects.get(pk=commentid)
		if story.poll:
			polls = Poll.objects.filter(story_id=commentid)
			for poll in polls:
				total_votes += poll.score
	except Stories.DoesNotExist:
		try:
			comments = HNComments.objects.get(id=commentid).get_descendants(True)
		except HNComments.DoesNotExist:
			raise Http404
	first_node = comments[0]
	return render_to_response('templates/comments.html', {'nodes': comments, 'story': story, 'first_node': first_node, 'polls': polls, 'total_votes': total_votes}, context_instance)


def command(request, command):
	# Secure this with some admin login
	# Although there isn't really anything bad you can do with it
	if command == 'migrate':
		management.call_command('migrate', all_apps=True)
		response = 'Command executed'
	elif command == 'collectstatic':
		management.call_command('collectstatic', interactive=False)
		response = 'Command executed'
	else:
		response = 'Command not found'
	return HttpResponse(response)
