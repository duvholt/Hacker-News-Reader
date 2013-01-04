from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.template import RequestContext
import reader.cache as cache
from reader.models import Stories, HNComments, Poll
from django.core import management
import reader.utils as utils
from django.core.urlresolvers import reverse


# This is not a real view, but is used from other views
def custom_message_view(request, message, context_instance):
	response = render_to_response("templates/message.html", {'message': message}, context_instance)
	return response


def index(request, story_type='news', json=False):
	limit = request.GET.get('limit', None)
	page = int(request.GET.get('page', 1))
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
	context_instance = RequestContext(request)
	stories = None
	try:
		cache.update_stories(story_type=story_type, over_filter=over)
		stories = cache.stories(page, limit, story_type=story_type, over_filter=over)
	except utils.ShowError, e:
		message = utils.UserMessage(e.value)
		message.url = reverse('index')
		return custom_message_view(request, message, context_instance)
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
	if json:
		template = 'templates/index_json.html'
	else:
		template = 'templates/index.html'
	response = render_to_response(template, {"stories": stories, "pages": pages, 'limit': limit}, context_instance)
	response.set_cookie('stories_limit', limit)
	return response


def comments(request, commentid, json=False):
	context_instance = RequestContext(request)
	# Context
	c = {'story': None, 'polls': None, 'lastpoll': None, 'total_votes': 0}
	try:
		cache.update_comments(comment_id=commentid)
		c['nodes'] = cache.comments(commentid)
	except utils.ShowError, e:
		message = utils.UserMessage(e.value)
		message.url = reverse('index')
		return custom_message_view(request, message, context_instance)
	try:
		c['story'] = Stories.objects.get(pk=commentid)
		if c['story'].poll:
			c['polls'] = Poll.objects.filter(story_id=commentid).order_by('id')
			for poll in c['polls']:
				c['total_votes'] += poll.score
	except Stories.DoesNotExist:
		try:
			c['nodes'] = HNComments.objects.get(id=commentid).get_descendants(True)
			if c['nodes'][0]:
				try:
					c['story'] = Stories.objects.get(pk=c['nodes'][0].story_id)
				except Stories.DoesNotExist:
					c['story'] = None
			c['perma'] = True
		except HNComments.DoesNotExist:
			raise Http404
	if json:
		template = 'templates/comments_json.html'
	else:
		template = 'templates/comments.html'
	return render_to_response(template, c, context_instance)


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
