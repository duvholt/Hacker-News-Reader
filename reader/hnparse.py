from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from django.db.models import F
from middleware import get_request
from models import Stories, HNComments, StoryCache, HNCommentsCache, Poll, UserInfo
from requests.compat import unquote
import datetime
import fetch
import logging
import re
import time
import utils


logger = logging.getLogger(__name__)


class CouldNotParse(Exception):
	def __init__(self, value='Failed to parse'):
		logger.error(value)

def is_event(soup):
	# Sometimes HN has special event link
	return True if soup.find('span', {'class': 'pagetop'}) else False


def stories(story_type, over_filter):
	soup = fetch.stories(story_type=story_type, over_filter=over_filter)
	# HN markup is odd. Basically every story use three rows each
	i = 1
	if is_event(soup.html.body.table.find_all('table')[1]):
		i += 1
	stories_soup = soup.html.body.table.find_all('table')[i].find_all("tr")[::3]
	# Scraping all stories
	for story_soup in stories_soup:
		try:
			story = story_info(story_soup)
			story.story_type = story_type
			story.poll = F('poll')
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


def comments(itemid, cache_minutes=20):
	# start_time = timezone.now()
	soup = fetch.comments(itemid=itemid)
	try:
		i = 1
		if is_event(soup.html.body.table.find_all('table')[1]):
			i += 1
		story_soup = soup.html.body.table.find_all('table')[i].find('tr')
		print story_soup
		if not story_soup:
			raise utils.ShowAlert('Item not found')
	except AttributeError:
		# Story does not exist
		raise utils.ShowAlert('Item not found')
	if story_soup.findNext('tr') and story_soup.findNext('tr').find('td', {'class': 'subtext'}):
		# Updating story info
		try:
			story = story_info(story_soup)
		except CouldNotParse:
			raise utils.ShowAlert('Story or comment deleted')
		parent_object = None
		permalink = False
		story_id = itemid
	else:
		# For permalinked comments
		try:
			# If comment already is in db get the info
			parent_object = HNComments.objects.get(id=itemid)
			if parent_object.cache + datetime.timedelta(minutes=cache_minutes) < timezone.now():
				try:
					traverse_comment(story_soup.parent, parent_object.parent, parent_object.story_id, perma=True)
				except CouldNotParse:
					pass
				parent_object = HNComments.objects.get(id=itemid)
		except HNComments.DoesNotExist:
			# Since the comment doesn't exist we have to improvise with the data a bit
			# Story is is not provided for permalinked comments, but parent id is
			# Story id will therefore temporarely be set to the comment id
			try:
				traverse_comment(story_soup.parent, None, itemid, perma=True)
			except CouldNotParse:
				return
			parent_object = HNComments.objects.get(id=itemid)
		story_id = parent_object.story_id
		permalink = True
		story = None
	poll = False
	if story:
		poll_table = story_soup.parent.find('table')
		if poll_table:
			poll = True
			poll_update(story.id, poll_table)
			story.poll = True
		selfpost_info = story_soup.parent.find_all('tr', {'style': 'height:2px'})
		if selfpost_info:
			story.selfpost_text = utils.html2markup(selfpost_info[0].next_sibling.find_all('td')[1].decode_contents())
		else:
			story.selfpost_text = ''
		story.save()
	if story or permalink:
		# Updating cache
		HNCommentsCache(id=itemid, time=timezone.now()).save()
		# If there is a poll there will be an extra table before comments
		i = 2
		if is_event(soup.html.body.table.find_all('table')[1]):
			i += 1
		if poll:
			i += 1
		# Traversing all top comments
		comments_soup = soup.html.body.table.find_all('table')[i].find_all('table')
		with transaction.commit_on_success():
			for comment_soup in comments_soup:
				td_default = comment_soup.tr.find('td', {'class': 'default'})
				# Converting indent to a more readable format (0, 1, 2...)
				indenting = int(td_default.previous_sibling.previous_sibling.img['width'], 10) / 40
				if indenting == 0:
					try:
						traverse_comment(comment_soup, parent_object, story_id)
					except CouldNotParse:
						continue
		# Slow
		# HNComments.objects.filter(cache__lt=start_time, story_id=itemid).update(dead=True)

def story_info(story_soup):
	if not story_soup.find('td'):
		raise CouldNotParse
	title = story_soup('td', {'class': 'title'})[-1]
	subtext = story_soup.find_next('tr').find('td', {'class': 'subtext'})
	# Dead post
	if not subtext.find_all('a'):
		raise CouldNotParse
	story = Stories()
	if title.next == ' [dead] ':
		story.dead = True
		story.url = ''
	else:
		story.url = unquote(title.find('a')['href'])
	story.title = title.find('a').contents[0]
	# Check for domain class
	if title.find('span', {'class': 'comhead'}):
		story.selfpost = False
	else:
		# No domain provided, must be a selfpost
		story.selfpost = True
		story.url = ''
	story.score = int(re.search(r'(\d+) points?', unicode(subtext.find("span"))).group(1))
	story.username = subtext.find('a').find(text=True)
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
	story.id = int(re.search('item\?id=(\d+)$', subtext.find_all('a')[1]['href']).group(1))
	story.cache = timezone.now()
	username = get_request().session.get('username', None)
	if username:
		# Adding vote auth to session
		userdata = get_request().session.setdefault('userdata', {}).setdefault(username, {})
		try:
			auth_code = re.search(r'&auth=([a-z0-9]+)&whence', story_soup.a['href']).group(1)
		except (TypeError, AttributeError):
			auth_code = None
		userdata.setdefault('votes', {})[str(story.id)] = auth_code
		get_request().session.modified = True
	return story


def traverse_comment(comment_soup, parent_object, story_id, perma=False):
	comment = HNComments()
	# Comment <td> container shortcut
	td_default = comment_soup.tr.find('td', {'class': 'default'})
	# Retrieving comment id from the permalink
	try:
		comment.id = int(re.search(r'item\?id=(\d+)$', td_default.find_all('a')[1]['href']).group(1), 10)
	except IndexError:
		raise CouldNotParse('Comment is dead')
	comment.username = td_default.find('a').find(text=True)
	# Get html contents of the comment excluding <span> and <font>
	if td_default.find('span', {'class': 'dead'}):
		comment.dead = True
		comment.text = utils.html2markup(td_default.find('span', {'class': 'comment'}).span.decode_contents())
		hex_color = '#000000'
	else:
		comment.dead = False
		# TODO: BS4 doesn't handle <i> split over paragraphs.
		# Therefore there is a bug that will only add italics on the first paragraph
		comment.text = utils.html2markup(td_default.find('span', {'class': 'comment'}).find('font').decode_contents())
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
		# Forcing comment to be updated next time, since it doesn't have proper values
			cache = timezone.now() - datetime.timedelta(days=1)
			parent_object = HNComments(id=parent_id, username='', parent=None, cache=cache)
			parent_object.save()
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
	comment.save()
	HNCommentsCache(id=comment.id, time=timezone.now()).save()

	username = get_request().session.get('username', None)
	if username:
		# Adding vote auth to session
		userdata = get_request().session.setdefault('userdata', {}).setdefault(username, {})
		try:
			auth_code = re.search(r'&auth=([a-z0-9]+)&whence', comment_soup.find_all('td', {'valign': 'top'})[0].a['href']).group(1)
		except (TypeError, AttributeError):
			auth_code = None
		userdata.setdefault('votes', {})[str(comment.id)] = auth_code
		get_request().session.modified = True

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
	soup = fetch.userpage(username=username)
	try:
		i = 1
		if is_event(soup.html.body.table.find_all('table')[1]):
			i += 1
		userdata = soup.html.body.table.find_all('table')[i].find_all('tr')
	except AttributeError:
		raise CouldNotParse('Couldn\'t get userdata' + username)
	created = utils.parse_time(userdata[1].find_all('td')[1].decode_contents())
	try:
		avg = Decimal(userdata[3].find_all('td')[1].decode_contents())
	except InvalidOperation:
		avg = 0
	# If user is logged in there will be an editable textarea instead of just text
	if userdata[4].find_all('td')[1].textarea:
		about = userdata[4].find_all('td')[1].textarea.decode_contents()
	else:
		about = utils.html2markup(userdata[4].find_all('td')[1].decode_contents())

	UserInfo(
		username=username,
		created=created,
		karma=int(userdata[2].find_all('td')[1].decode_contents(), 10),
		avg=avg,
		about=about,
		cache=timezone.now()
	).save()


def poll_update(story_id, polls, userdata=None):
	for poll in polls.find_all('tr')[::3]:
		Poll(
			name=poll.find_all('td')[1].text,
			score=int(re.search(r'(\d+) points?', poll.find_next('tr').find_all('td')[1].text).group(1)),
			id=poll.find_next('tr').find_all('td')[1].span.span['id'].lstrip('score_'),
			story_id=story_id
		).save()
