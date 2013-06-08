from reader.models import Stories, HNComments, StoryCache, HNCommentsCache, Poll, UserInfo
import reader.utils as utils
from django.conf import settings
from django.utils import timezone
from bs4 import BeautifulSoup
import httplib
import urllib2
import time
import datetime
import lxml
import re
from decimal import Decimal, InvalidOperation
import logging

# Getting rid of unused warning for lxml
lxml = lxml
logger = logging.getLogger(__name__)


class Fetch(object):
# Kinda silly to use a class with static only methods
	@staticmethod
	def comments(commentid):
		return Fetch.read('item?id=' + unicode(commentid))

	@staticmethod
	def stories(story_type, over_filter=None):
		if story_type == 'news' and isinstance(over_filter, int):
			return Fetch.read('over?points=' + unicode(over_filter))
		elif story_type in ['best', 'active', 'newest', 'ask', 'news']:
			return Fetch.read(story_type)

	@staticmethod
	def userpage(username):
		return Fetch.read('user?id=' + unicode(username))

	@staticmethod
	def read(url):
		try:
			opener = urllib2.build_opener()
			opener.addheaders = [('User-agent', 'Hacker News Reader (' + settings.DOMAIN_URL + ')')]
			response = opener.open('http://news.ycombinator.com/' + url)
			doc = response.read()
			if re.match(r'^We\'ve limited requests for old items', doc):
				raise utils.OldItemDenied('Limited request')
			elif re.match(r'^We\'ve limited requests for this url', doc):
				raise utils.UrlDenied('Limited request')
		except (urllib2.URLError, httplib.BadStatusLine):
			raise utils.ShowError('Could not connect to news.ycombinator.com, try again later.<br>If this error persists please contact the developer.')
		except utils.OldItemDenied:
			raise utils.ShowError('Requests have been limited for old items. It might take a while before you can access this.')
		except utils.UrlDenied:
			raise utils.ShowError('Requests have been limited for this page. It might take a while before you can access this.')
		return BeautifulSoup(doc, 'lxml', from_encoding='utf-8')


class CouldNotParse(Exception):
	def __init__(self, value='Failed to parse'):
		logger.error(value)


def stories(story_type, over_filter):
	soup = Fetch.stories(story_type=story_type, over_filter=over_filter)
	# HN markup is odd. Basically every story use three rows each
	stories_soup = soup.html.body.table.find_all('table')[1].find_all("tr")[::3]
	# Scraping all stories
	for story_soup in stories_soup:
		try:
			story = story_info(story_soup)
			story.story_type = story_type
			story.cache = timezone.now()
			story.save()
		except CouldNotParse:
			continue
	# Updating cache
	if story_type == 'news' and over_filter:
		over = over_filter
	else:
		over = None
	story_cache, created = StoryCache.objects.get_or_create(name=story_type, over=over)
	story_cache.time = timezone.now()
	story_cache.save()


def comments(commentid, cache_minutes=20):
	start_time = timezone.now()
	soup = Fetch.comments(commentid=commentid)
	try:
		story_soup = soup.html.body.table.find_all('table')[1].find('tr')
	except AttributeError:
		# Story does not exist
		raise CouldNotParse('Story not found: ' + str(commentid))
	if story_soup.findNext('tr').find('td', {'class': 'subtext'}):
		# Updating story info
		try:
			story = story_info(story_soup)
		except CouldNotParse:
			raise utils.ShowError('Story or comment deleted')
		parent_object = None
		permalink = False
		story_id = commentid
	else:
		# For permalinked comments
		try:
			# If comment already is in db get the info
			parent_object = HNComments.objects.get(id=commentid)
			if parent_object.cache + datetime.timedelta(minutes=cache_minutes) < timezone.now():
				try:
					traverse_comment(story_soup.parent, parent_object.parent, parent_object.story_id, perma=True)
				except CouldNotParse:
					pass
				parent_object = HNComments.objects.get(id=commentid)
		except HNComments.DoesNotExist:
			# Since the comment doesn't exist we have to improvise with the data a bit
			# Story is is not provided for permalinked comments, but parent id is
			# Story id will therefore temporarely be set to the comment id
			traverse_comment(story_soup.parent, None, commentid, perma=True)
			parent_object = HNComments.objects.get(id=commentid)
		story_id = parent_object.story_id
		permalink = True
		story = None
	poll = False
	if story:
		poll_table = story_soup.parent.find('table')
		if poll_table:
			poll = True
			poll_update(story.id, poll_table)
			story.poll = poll
		selfpost_info = story_soup.parent.find_all('tr', {'style': 'height:2px'})
		if selfpost_info:
			story.selfpost_text = utils.html2markup(selfpost_info[0].next_sibling.find_all('td')[1].decode_contents())
		else:
			story.selfpost_text = ''
		story.save()
	if story or permalink:
		# Updating cache
		HNCommentsCache(id=commentid, time=timezone.now()).save()
		# If there is a poll there will be an extra table before comments
		i = 2
		if poll:
			i += 1
		# Traversing all top comments
		comments_soup = soup.html.body.table.find_all('table')[i].find_all('table')
		for comment_soup in comments_soup:
			td_default = comment_soup.tr.find('td', {'class': 'default'})
			# Converting indent to a more readable format (0, 1, 2...)
			indenting = int(td_default.previous_sibling.previous_sibling.img['width'], 10) / 40
			if indenting == 0:
				try:
					traverse_comment(comment_soup, parent_object, story_id)
				except CouldNotParse:
					continue
		HNComments.objects.filter(cache__lt=start_time, story_id=commentid).update(dead=True)


def story_info(story_soup):
	if not story_soup.find('td'):
		raise CouldNotParse
	title = story_soup('td', {'class': 'title'})[-1]
	subtext = story_soup.find_next('tr').find('td', {'class': 'subtext'})
	# Dead post
	if not subtext.find_all("a"):
		raise CouldNotParse
	story = Stories()
	story.url = urllib2.unquote(title.find('a')['href'])
	story.title = title.find('a').contents[0]
	# Check for domain class
	if title.find('span', {'class': 'comhead'}):
		story.selfpost = False
	else:
		# No domain provided, must be a selfpost
		story.selfpost = True
		story.url = ''
	story.score = int(re.search(r'(\d+) points?', unicode(subtext.find("span"))).group(1))
	story.username = ''.join(subtext.find_all("a")[0])
	try:
		story.comments = int(re.search(r'(\d+) comments?', unicode(subtext.find_all("a")[1])).group(1))
	except AttributeError:
		# Comments are not always shown (old submissions or ones with 0 comments)
		story.comments = 0
	# Unfortunalely HN doesn't show any form timestamp other than "x hours"
	# meaning that the time scraped is only approximately correct.
	story.time = utils.parse_time(subtext.find_all("a")[1].previous_sibling + ' ago')
	# parsedatetime doesn't have any built in support for DST
	if time.localtime().tm_isdst:
		story.time = story.time + datetime.timedelta(hours=-1)
	story.id = re.search('item\?id=(\d+)$', subtext.find_all("a")[1]['href']).group(1)
	story.cache = timezone.now()
	return story


def traverse_comment(comment_soup, parent_object, story_id, perma=False):
	comment = HNComments()
	# Comment <td> container shortcut
	td_default = comment_soup.tr.find('td', {'class': 'default'})
	# Retrieving comment id from the permalink
	try:
		comment.id = int(re.search(r'item\?id=(\d+)$', td_default.find_all('a')[1]['href']).group(1), 10)
	except IndexError:
		raise CouldNotParse('Couldn\'t get comment id' + str(story_id))
	comment.username = td_default.find('a').find(text=True)
	# Get html contents of the comment excluding <span> and <font>
	comment.text = utils.html2markup(td_default.find('span', {'class': 'comment'}).font.decode_contents())
	hex_color = td_default.find('span', {'class': 'comment'}).font['color']
	# All colors are in the format of #XYXYXY, meaning that they are all grayscale.
	# Get percent by grabbing the red part of the color (#XY)
	comment.hiddenpercent = int(re.search(r'^#(\w{2})', hex_color).group(1), 16) / 2.5
	comment.hiddencolor = hex_color
	comment.time = utils.parse_time(td_default.find('a').next_sibling + ' ago')
	# parsedatetime doesn't have any built in support for DST
	if time.localtime().tm_isdst == 1:
		comment.time = comment.time + datetime.timedelta(hours=-1)
	# Some extra trickery for permalinked comments
	if perma:
		parent_id = int(re.search(r'item\?id=(\d+)$', td_default.find_all('a')[2]['href']).group(1), 10)
		try:
			# Checking if the parent object is in the db
			parent_object = HNComments.objects.get(pk=parent_id)
			story_id = parent_object.story_id
		except HNComments.DoesNotExist:
			parent_object = None
			# story_id is at this moment actually comment id of the parent object.
			# Trying to correct this by checking for actualy story_id in the db
			try:
				story_id = HNComments.objects.get(pk=story_id).story_id
			except HNComments.DoesNotExist:
				# Oops, looks like we'll just store a fake one for now
				pass
	comment.story_id = story_id
	comment.cache = timezone.now()
	comment.parent = parent_object
	if perma and not parent_object and parent_id:
		# Forcing comment to be updated next time, since it doesn't have proper values
		cache = timezone.now() - datetime.timedelta(days=1)
		parent_object = HNComments(id=parent_id, username='', parent=None, cache=cache)
		parent_object.save()
		comment.parent = parent_object
	comment.save()
	HNCommentsCache(id=comment.id, time=timezone.now()).save()

	# Traversing over child comments:
	# Since comments aren't actually children in the HTML we will have to parse all the siblings
	# and check if they have +1 indent indicating that they are a child.
	# However if a following comment has the same indent value it is not a child and neither a sub child
	# meaning that all child comments have been parsed.
	if not perma:
		indenting = int(td_default.previous_sibling.previous_sibling.img['width'], 10) / 40
		for sibling_soup in comment_soup.parent.parent.find_next_siblings('tr'):
			sibling_table = sibling_soup.table
			# Comment pages with a "More" link at the bottom will have two extra trs without a table
			if sibling_table:
				sibling_td_default = sibling_table.tr.find('td', {'class': 'default'})
				sibling_indenting = int(sibling_td_default.previous_sibling.previous_sibling.img['width'], 10) / 40
				if sibling_indenting == indenting + 1:
					try:
						traverse_comment(sibling_table, comment, story_id)
					except CouldNotParse:
						continue
				if sibling_indenting == indenting:
					break
			elif sibling_soup.find('td', {'class': 'title'}):
				# TODO Add support for loading more comments
				continue


def userpage(username):
	soup = Fetch.userpage(username=username)
	try:
		userdata = soup.html.body.table.find_all('table')[1].find_all('tr')
	except AttributeError:
		raise CouldNotParse('Couldn\'t get userdata' + username)
	created = utils.parse_time(userdata[1].find_all('td')[1].decode_contents())
	try:
		avg = Decimal(userdata[3].find_all('td')[1].decode_contents())
	except InvalidOperation:
		avg = 0
	UserInfo(
		username=username,
		created=created,
		karma=int(userdata[2].find_all('td')[1].decode_contents(), 10),
		avg=avg,
		about=utils.html2markup(userdata[4].find_all('td')[1].decode_contents()),
		cache=timezone.now()
	).save()


def poll_update(story_id, poll_soup):
	for poll_element in poll_soup.find_all('tr')[::3]:
		Poll(
			name=poll_element.find_all('td')[1].div.font.decode_contents(),
			score=int(re.search(r'(\d+) points?', poll_element.find_next('tr').find_all('td')[1].span.span.decode_contents()).group(1)),
			id=poll_element.find_next('tr').find_all('td')[1].span.span['id'].lstrip('score_'),
			story_id=story_id
		).save()
