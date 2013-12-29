from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils.dateformat import format
from django.views.generic import TemplateView
from middleware import get_request
from models import Stories, HNComments, Poll, UserInfo
import cache
import fetch
import hnparse
import json
import operator
import requests
import utils
import settings

# Warning levels: error, success, info and default (empty)


class JSONResponseMixin(object):
	"""
	A mixin that can be used to render a JSON response.
	"""
	response_class = HttpResponse

	def render_view(self, **response_kwargs):
		"""
		Returns a JSON response, transforming 'context' to make the payload.
		"""
		response_kwargs['content_type'] = 'application/json'
		return self.response_class(self.convert_context_to_json(), **response_kwargs)

	def convert_context_to_json(self):
		self.prepare_context()
		if 'alerts' in self.context:
			for alert in self.context['alerts']:
				if alert['level'] == 'danger':
					return json.dumps({'alerts': context['alerts']})
			# Remove if empty
			if not self.context['alerts']:
				self.context.pop('alerts')
		return json.dumps(self.context)

	def prepare_context(self):
		pass

	def clean_context(self):
		"""
		Used to clear up the context so it can be redone
		"""
		if 'alerts' in self.context:
			self.context = {'alerts': self.context['alerts']}
		else:
			self.context = {}


class ContextView(TemplateView):
	context = {'alerts': []}

	def render_view(self, *args, **kwargs):
		kwargs['context'] = self.context
		return super(ContextView, self).render_to_response(*args, **kwargs)


class IndexView(ContextView):
	template_name = 'templates/index.html'

	def get(self, request, *args, **kwargs):
		story_type = kwargs.get('story_type', 'news')
		try:
			page = int(request.GET.get('page'))
		except (ValueError, TypeError):
			page = 1

		try:
			over = int(request.GET.get('over'))
		except (ValueError, TypeError):
			over = None

		limit = request.GET.get('limit')
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
			self.context['alerts'].append({'message': e.message, 'level': e.level})
			return self.render_view()

		pages = self.get_active_pages(stories, page)

		self.context.update({'stories': stories, 'pages': pages, 'limit': limit, 'cache': cachetime})
		response = self.render_view()
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
	def prepare_context(self):
		stories = self.context['stories']
		self.clean_context()
		self.context['stories'] = []
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
				story_json['domain'] = utils.domain(story.url)
			self.context['stories'].append(story_json)
		self.context['page'] = {'current': stories.number, 'total': stories.paginator.num_pages}


class CommentsView(ContextView):
	template_name = 'templates/comments.html'

	def get(self, request, *args, **kwargs):
		self.comment_id = kwargs['commentid']
		if self.comment_id:
			try:
				self.comment_id = int(self.comment_id, 10)
			except ValueError:
				self.comment_id = None
		self.context.update({'story': None, 'polls': None, 'total_votes': 0})
		try:
			cache.update_comments(commentid=self.comment_id)
		except utils.ShowAlert, e:
			self.context['alerts'].append({'message': e.message, 'level': e.level})
		try:
			self.context['story'] = Stories.objects.get(pk=self.comment_id)
			if self.context['story'].poll:
				self.context['polls'] = Poll.objects.filter(story_id=self.comment_id).order_by('id')
				for poll in self.context['polls']:
					self.context['total_votes'] += poll.score
			self.context['comments'] = []
			self.context['comments'] = self.full_comments_list()
		except Stories.DoesNotExist:
			try:
				comment = HNComments.objects.get(id=self.comment_id)
				self.context['comments'] = self.permalink_comments_list(comment)
				if comment:
					try:
						self.context['story'] = Stories.objects.get(pk=comment.story_id)
					except Stories.DoesNotExist:
						self.context['story'] = None
				self.context['perma'] = True
			except HNComments.DoesNotExist:
				self.context['alerts'].append({'message': 'Item not found'})
		username = request.session.get('username')
		if username:
			userdata = request.session.setdefault('userdata', {}).setdefault(username, {})
			self.context['votes'] = userdata.setdefault('votes', [])
		return self.render_view()

	def full_comments_list(self):
		return self.get_children(list(HNComments.objects.filter(story_id=self.comment_id)))

	def permalink_comments_list(self, comment):
		comments = [(comment, {'level': 0, 'open': True, 'close': []})]
		hncomments = list(HNComments.objects.filter(story_id=comment.story_id))
		children = self.get_children(hncomments, parent_id=comment.id, level=1)
		comments += children
		if not children:
			comments[0][1]['close'] = [1]
		return comments

	def get_children(self, comments, parent_id=None, level=0, root_close=0):
		# Inspired by django-mptt's tree_info and treebeard's get_annotated_list
		result = []
		roots = [comment for comment in comments if comment.parent_id == parent_id]
		order = HNComments._meta.ordering
		roots_sorted = sorted(roots, key=operator.attrgetter(*order))
		num_roots = len(roots_sorted)
		for index, root in enumerate(roots_sorted):
			info = {
			'level': level,
			'open': index == 0,
			'close': [],
			}
			close = root_close
			if index == (num_roots - 1):
				close += 1
			else:
				close = 0
			children = self.get_children(comments, root.id, level=level + 1, root_close=close)
			if index == (num_roots - 1) and not children:
				info['close'] = list(range(0, close))
			result.append((root, info))
			result += children
		return result

	def list_to_nested(self, comments):
		# Inspired by django-mptt's cache_tree_children
		current_path, root_nodes = [], []
		for comment, info in comments:
			comment._children = []
			while len(current_path) > info['level']:
				current_path.pop(-1)
			# Root node
			if info['level'] == 0:
				root_nodes.append(comment)
			else:
				current_path[-1]._children.append(comment)
			current_path.append(comment)
		return root_nodes


class CommentsJsonView(JSONResponseMixin, CommentsView):

	def prepare_context(self):
		story = self.context.get('story')
		polls = self.context.get('polls')
		total_votes = self.context.get('total_votes')
		root_comments = self.list_to_nested(self.context.get('comments'))
		self.clean_context()
		if story:
			self.context['story'] = {
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
				self.context['story']['selfpost_text'] = story.selfpost_text
			else:
				self.context['story']['url'] = story.url
				self.context['story']['domain'] = utils.domain(story.url)
			if story.dead:
				self.context['story']['dead'] = True
		if polls:
			self.context['polls'] = []
			for poll in polls:
				self.context['polls'].append({
					'name': poll.name,
					'votes': poll.score,
					'percentage': utils.poll_percentage(poll.score, total_votes, 2)
				})
		self.context['comments'] = []
		# recursive_comment_to_dict and list_to_nested could be combined to reduce looping
		for root_comment in root_comments:
			self.context['comments'].append(self.recursive_comment_to_dict(root_comment, bool(story)))
		return self.context

	def recursive_comment_to_dict(self, comment, story):
		result = {
			'id': comment.id,
			'username': comment.username,
			'time': format(comment.time, 'r'),
			'time_unix': format(comment.time, 'U'),
			'hiddenpercent': comment.hiddenpercent,
			'text': comment.text,
			'cache': format(comment.cache, 'r'),
			'cache_unix': format(comment.cache, 'U')
		}
		if comment.parent_id:
			result['parent'] = comment.parent_id
		elif not story:
			result['parent'] = comment.story_id
		if comment.dead:
			result['dead'] = True
		children = [self.recursive_comment_to_dict(child, story) for child in comment._children]
		if children:
			result['children'] = children
		return result


class VoteView(ContextView):
	def get(self, request, *args, **kwargs):
		try:
			vote_id = int(kwargs.get('id'))
		except (ValueError, TypeError):
			vote_id = None
		direction = request.GET.get('dir', 'up')
		try:
			if type(vote_id) is not int:
				raise utils.ShowAlert('Not a valid id')
			elif 'username' not in request.session:
				raise utils.ShowAlert('You\'re not logged in')
			else:
				username = request.session['username']
				userdata = request.session.setdefault('userdata', {}).setdefault(username, {})
				# Using str() because keys in session is stored as string
				if str(vote_id) in userdata.setdefault('votes', {}):
					auth = userdata['votes'][str(vote_id)]
				else:
					# Auth code not found in cache, going to have to manually get it from comment
					hnparse.comments(vote_id, 0)
					# Not using str() here because keys are only converted to string on save
					if vote_id in userdata.setdefault('votes', {}):
						auth = userdata['votes'][vote_id]
					else:
						# Giving up
						raise utils.ShowAlert('Unable to get auth id')
				if auth is None:
					raise utils.ShowAlert('Already voted')
				payload = {'for': vote_id, 'dir': direction, 'by': username, 'auth': auth}
				h = {'user-agent': 'Hacker News Reader (' + settings.DOMAIN_URL + ')'}
				c = {'user': request.session['usercookie']}
				r = requests.get('https://news.ycombinator.com/vote', params=payload, headers=h, cookies=c)
				if r.status_code != requests.codes.ok:
					raise utils.ShowAlert('Unknown error')
				elif r.text == 'User mismatch.':
					raise utils.ShowAlert('Failed to vote due to wrong authcode')
				elif r.text == 'Can\'t make that vote.':
					raise utils.ShowAlert('Already voted or missing permissions to up/down vote', level='warning')
				elif r.text == 'No such item.':
					raise utils.ShowAlert('No such item')
				elif r.text != '':
					raise utils.ShowAlert(r.text)
				else:
					# Setting auth to None to signify that item has been voted on
					userdata['votes'][str(vote_id)] = None
					request.session.modified = True
					raise utils.ShowAlert('Voted successfully', level='success')
		except utils.ShowAlert, e:
			self.context['alerts'].append({'message': e.message, 'level': e.level})
		# TODO: Redirect to referrer
		return self.render_view()


class VoteJsonView(JSONResponseMixin, VoteView):
	pass


class UserView(ContextView):
	template_name = 'templates/user.html'

	def get(self, request, *args, **kwargs):
		username = kwargs['username']
		try:
			cache.update_userpage(username=username)
			self.context['userinfo'] = cache.userinfo(username)
		except UserInfo.DoesNotExist:
			self.context['alerts'].append({'message': 'User not found'})
		except utils.ShowAlert, e:
			self.context['alerts'].append({'message': e.message, 'level': e.level})
		return self.render_view()


class UserJsonView(JSONResponseMixin, UserView):
	def prepare_context(self):
		userinfo = self.context.get('userinfo', None)
		self.clean_context()
		if userinfo:
			self.context['user'] = {
				'username': userinfo.username,
				'created': format(userinfo.created, 'r'),
				'created_unix': format(userinfo.created, 'U'),
				'karma': userinfo.karma,
				'avg': round(userinfo.avg, 2),
				'cache': format(userinfo.cache, 'r'),
				'cache_unix': format(userinfo.cache, 'U')
			}
			if userinfo.about:
				self.context['user']['about'] = userinfo.about


class LoginView(ContextView):
	template_name = 'templates/login.html'

	def get(self, request, *args, **kwargs):
		return self.render_view()

	def post(self, request):
		if all(key in request.POST for key in ['username', 'password']):
			username = request.POST['username']
			password = request.POST['password']
			if username and password:
				soup = fetch.login()
				fnid = soup.find('input', {'type': 'hidden'})['value']
				payload = {'fnid': fnid, 'u': username, 'p': password}
				s = requests.Session()
				headers = {'user-agent': 'Hacker News Reader (' + settings.DOMAIN_URL + ')'}
				s.post('https://news.ycombinator.com/y', data=payload, headers=headers)
				if 'user' in s.cookies:
					request.session['username'] = username
					request.session['usercookie'] = s.cookies['user']
					self.context['alerts'].append({'message': 'Logged in as ' + username, 'level': 'success'})
				else:
					self.context['alerts'].append({'message': 'Username or password wrong'})
			else:
				self.context['alerts'].append({'message': 'Username or password missing'})
		return self.render_view()


class LogoutView(ContextView):
	def get(self, request, *args, **kwargs):
		try:
			del request.session['username']
			del request.session['usercookie']
		except KeyError:
			pass
		return redirect('index')
