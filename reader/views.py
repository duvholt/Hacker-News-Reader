from django.shortcuts import redirect
from django.http import HttpResponse
import reader.cache as cache
from reader.models import Stories, HNComments, Poll, UserInfo
import reader.utils as utils
from reader.hnparse import Fetch
import requests
from django.views.generic import TemplateView
import json
from django.utils.dateformat import format
from utils import domain, poll_percentage
from mptt.templatetags.mptt_tags import cache_tree_children

# Warning levels: error, success, info and default (empty)


class JSONResponseMixin(object):
	"""
	A mixin that can be used to render a JSON response.
	"""
	response_class = HttpResponse

	def render_to_response(self, context, **response_kwargs):
		"""
		Returns a JSON response, transforming 'context' to make the payload.
		"""
		response_kwargs['content_type'] = 'application/json'
		return self.response_class(self.convert_context_to_json(context), **response_kwargs)

	def convert_context_to_json(self, context):
		if 'alerts' in context:
			for alert in context['alerts']:
				if alert['level'] == 'error':
					return	json.dumps({'alerts': context['alerts']})
			# Remove if empty
			if not context['alerts']:
				context.pop('alerts')
		return json.dumps(context)

	def clean_context(self, context):
		"""
		Used to clear up the context so it can be redone
		"""
		if 'alerts' in context:
			context = {'alerts': context['alerts']}
		else:
			context = {}
		return context


class ContextView(TemplateView):
	def get_context_data(self, **kwargs):
		if 'alerts' not in kwargs:
			kwargs['alerts'] = []
		return kwargs


class IndexView(ContextView):
	template_name = 'templates/index.html'

	def get(self, request, *args, **kwargs):
		context = super(IndexView, self).get_context_data()
		story_type = kwargs.get('story_type', 'news')
		try:
			page = int(request.GET.get('page'))
		except (ValueError, TypeError):
			page = 1

		try:
			over = int(request.GET.get('over'))
		except (ValueError, TypeError):
			over = None

		limit = request.GET.get('limit', None)
		if not limit:
			limit = request.COOKIES.get('stories_limit')
		try:
			limit = int(limit)
		except (ValueError, TypeError):
			limit = 25

		try:
			cachetime = cache.update_stories(story_type=story_type, over_filter=over)
			stories = cache.stories(page, limit, story_type=story_type, over_filter=over)
		except utils.ShowAlert, e:
			context['alerts'].append({'message': e.message, 'level': e.level})
			return self.render_to_response(self.get_context_data(**context))

		pages = self.get_active_pages(stories, page)

		context.update({'stories': stories, 'pages': pages, 'limit': limit, 'cache': cachetime})
		response = self.render_to_response(self.get_context_data(**context))
		response.set_cookie('stories_limit', limit)
		return response

	def get_active_pages(self, stories, page):
		visible_pages = 6
		pages = stories.paginator.page_range
		if stories.paginator.num_pages > visible_pages:
			diff = visible_pages / 2
			if page > diff:
				left = page - diff
				right = page + diff
				if stories.paginator.num_pages - page < diff:
					left -= diff - (stories.paginator.num_pages - page)
			else:
				left = 0
				right = visible_pages
			pages = pages[left:right]
		return pages


class IndexJsonView(JSONResponseMixin, IndexView):
	def get_context_data(self, **kwargs):
		context = super(IndexJsonView, self).get_context_data(**kwargs)
		stories = context['stories']
		context = self.clean_context(context)
		context['stories'] = []
		for story in stories:
			story_json = {
			'id': story.id,
			'title': story.title,
			'selfpost': story.selfpost,
			'poll': story.poll,
			'username': story.username,
			'score': story.score,
			'comments': story.comments,
			'story_type': story.story_type,
			'time': format(story.time, 'r'),
			'time_unix': format(story.time, 'U'),
			'cache': format(story.cache, 'r'),
			'cache_unix': format(story.cache, 'U')
			}
			if not story.selfpost:
				story_json['url'] = story.url
				story_json['domain'] = domain(story.url)
			context['stories'].append(story_json)
		context['page'] = {'current': stories.number, 'total': stories.paginator.num_pages}
		return context


class CommentsView(ContextView):
	template_name = 'templates/comments.html'

	def get(self, request, *args, **kwargs):
		context = super(CommentsView, self).get_context_data()
		commentid = kwargs['commentid']
		if commentid:
			try:
				commentid = int(commentid, 10)
			except ValueError:
				commentid = None
		context.update({'story': None, 'polls': None, 'total_votes': 0})
		try:
			cache.update_comments(commentid=commentid)
		except utils.ShowAlert, e:
			context['alerts'].append({'message': e.message, 'level': e.level})
		try:
			context['story'] = Stories.objects.get(pk=commentid)
			# Using list() to force evaluation
			if context['story'].poll:
				context['polls'] = Poll.objects.filter(story_id=commentid).order_by('id')
				for poll in context['polls']:
					context['total_votes'] += poll.score
			context['nodes'] = list(cache.comments(commentid))
		except Stories.DoesNotExist:
			try:
				context['nodes'] = list(HNComments.objects.get(id=commentid).get_descendants(True))
				node_first = context['nodes'][0]
				if node_first:
					try:
						context['story'] = Stories.objects.get(pk=node_first.story_id)
					except Stories.DoesNotExist:
						context['story'] = None
				context['perma'] = True
			except HNComments.DoesNotExist:
				context['alerts'].append({'message': 'Item not found', 'level': 'error'})
		return self.render_to_response(self.get_context_data(**context))


class CommentsJsonView(JSONResponseMixin, CommentsView):

	def get_context_data(self, **kwargs):
		context = super(CommentsJsonView, self).get_context_data(**kwargs)
		story = context.get('story', None)
		polls = context.get('polls', None)
		total_votes = context.get('total_votes', None)
		root_comments = cache_tree_children(context.get('nodes', None))
		context = self.clean_context(context)
		if story:
			context['story'] = {
			'id': story.id,
			'title': story.title,
			'selfpost': story.selfpost,
			'poll': story.poll,
			'score': story.score,
			'username': story.username,
			'time': format(story.time, 'r'),
			'time_unix': format(story.time, 'U'),
			'comments': story.comments,
			'cache': format(story.cache, 'r'),
			'cache_unix': format(story.cache, 'U')
			}
			if story.selfpost:
				context['story']['selfpost_text'] = story.selfpost_text
			else:
				context['story']['url'] = story.url
				context['story']['domain'] = domain(story.url)
		if polls:
			context['polls'] = []
			for poll in polls:
				context['polls'].append({
				'name': poll.name,
				'votes': poll.score,
				'percentage': poll_percentage(poll.score, total_votes, 2)
				})
		context['comments'] = []
		for root_comment in root_comments:
			context['comments'].append(self.recursive_node_to_dict(root_comment, bool(story)))
		return context

	def recursive_node_to_dict(self, node, story):
		result = {
		'id': node.id,
		'username': node.username,
		'time': format(node.time, 'r'),
		'time_unix': format(node.time, 'U'),
		'hiddenpercent': node.hiddenpercent,
		'text': node.text,
		'cache': format(node.cache, 'r'),
		'cache_unix': format(node.cache, 'U')
		}
		if node.parent_id:
			result['parent'] = node.parent_id
		elif not story:
			result['parent'] = node.story_id
		children = [self.recursive_node_to_dict(child, story) for child in node.get_children()]
		if children:
			result['children'] = children
		return result


class UserView(ContextView):
	template_name = 'templates/user.html'

	def get(self, request, *args, **kwargs):
		context = super(UserView, self).get_context_data()
		username = kwargs['username']
		try:
			cache.update_userpage(username=username)
			context['userinfo'] = cache.userinfo(username)
		except UserInfo.DoesNotExist:
			context['alerts'].append({'message': 'User not found'})
		except utils.ShowAlert, e:
			context['alerts'].append({'message': e.message, 'level': e.level})
		return self.render_to_response(self.get_context_data(**context))


class UserJsonView(JSONResponseMixin, UserView):
	def get_context_data(self, **kwargs):
		context = super(UserJsonView, self).get_context_data(**kwargs)
		userinfo = context.get('userinfo', None)
		context = self.clean_context(context)
		if userinfo:
			context['user'] = {
			'username': userinfo.username,
			'created': format(userinfo.created, 'r'),
			'created_unix': format(userinfo.created, 'U'),
			'karma': userinfo.karma,
			'avg': round(userinfo.avg, 2),
			'cache': format(userinfo.cache, 'r'),
			'cache_unix': format(userinfo.cache, 'U')
			}
			if userinfo.about:
				context['user']['about'] = userinfo.about
		return context


class LoginView(ContextView):
	template_name = 'templates/login.html'

	def get(self, request, *args, **kwargs):
		context = super(LoginView, self).get_context_data()
		return self.render_to_response(self.get_context_data(**context))

	def post(self, request):
		context = super(LoginView, self).get_context_data()
		if all(key in request.POST for key in ['username', 'password']):
			username = request.POST['username']
			password = request.POST['password']
			if username and password:
				soup = Fetch.login()
				fnid = soup.find('input', {'type': 'hidden'})['value']
				payload = {'fnid': fnid, 'u': username, 'p': password}
				r = requests.post('https://news.ycombinator.com/x', data=payload)
				if 'user' in r.cookies:
					request.session['username'] = username
					request.session['usercookie'] = r.cookies['user']
					context['alerts'].append({'message': 'Logged in as ' + username, 'level': 'success'})
				else:
					context['alerts'].append({'message': 'Username or password wrong', 'level': 'error'})
			else:
				context['alerts'].append({'message': 'Username or password missing', 'level': 'error'})
		return self.render_to_response(self.get_context_data(**context))


class  LogoutView(ContextView):
	def get(self, request, *args, **kwargs):
		try:
			del request.session['username']
			del request.session['usercookie']
		except KeyError:
			pass
		return redirect('index')
