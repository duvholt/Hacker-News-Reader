from bs4 import BeautifulSoup
import urllib2
from django.utils import timezone
import parsedatetime.parsedatetime as pdt
import parsedatetime.parsedatetime_consts as pdc
import datetime
import re
from reader.models import Stories, HNComments, StoryCache, HNCommentsCache, Poll
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from collections import OrderedDict
import time
from tzlocal import get_localzone
import lxml
import reader.utils as utils


c = pdc.Constants()
p = pdt.Calendar(c)
tz = get_localzone()


def update_stories(cache_minutes=20, story_type='news', over_filter=0):
	try:
		if story_type == 'over':
			# Over points can have different values meaning that it can't be cached normal
			cachetime = StoryCache.objects.get(name=story_type, over=over_filter).time
		else:
			cachetime = StoryCache.objects.get(name=story_type).time
	except StoryCache.DoesNotExist:
		# Force updating cache
		cachetime = timezone.now() - datetime.timedelta(days=1)
	# More than cache_minutes since cache was updated
	if(cachetime + datetime.timedelta(minutes=cache_minutes) < timezone.now()):
		if story_type in ['best', 'active', 'newest', 'ask']:
			url = story_type
		elif story_type == 'news' and isinstance(over_filter, int):
			url = 'over?points=' + str(over_filter)
		else:
			url = 'news'
			story_type = 'news'
		try:
			doc = urllib2.urlopen('http://news.ycombinator.com/' + url).read()
		except urllib2.URLError:
			raise utils.CustomError('Could not connect to news.ycombinator.com, try again later')
		soup = BeautifulSoup(doc, 'lxml')
		# HN markup is odd. Basically every story use three rows each
		stories_soup = soup.html.body.table.findAll('table')[1].findAll("tr")[::3]
		updated_cache = False
		for story_soup in stories_soup:
			story = story_info(story_soup)
			if story:
				story_object = Stories(id=story['id'], title=story['title'],
								url=story['url'], score=story['score'], selfpost=story['selfpost'],
								domain=story['domain'], username=story['username'], comments=story['comments'],
								story_type=story_type, time=story['time'], cache=timezone.now())
				story_object.save()
				# Only update cache once
				if not updated_cache:
					if not story_type == 'over':
						story_cache = StoryCache.objects.get(name=story_type)
					else:
						story_cache, created = StoryCache.objects.get_or_create(name=story_type, over=over_filter)
					story_cache.time = timezone.now()
					story_cache.save()
					updated_cache = True


def update_comments(comment_id, cache_minutes=20):
	try:
		cachetime = HNCommentsCache.objects.get(pk=comment_id).time
	except HNCommentsCache.DoesNotExist:
		# Force updating cache
		cachetime = timezone.now() - datetime.timedelta(days=1)
	if(cachetime + datetime.timedelta(minutes=cache_minutes) < timezone.now()):
		doc = urllib2.urlopen('https://news.ycombinator.com/item?id=' + unicode(comment_id))
		soup = BeautifulSoup(doc, 'lxml')
		try:
			story_soup = soup.html.body.table.findAll('table')[1].find('tr')
		except AttributeError:
			# Story does not exist
			return False
		if story_soup.findNext('tr').find('td', {'class': 'subtext'}):
			# Updating story info
			story = story_info(story_soup)
			parent_object = None
			permalink = False
			story_id = comment_id
		else:
			# For permalinked comments
			try:
				# If comment already is in db get the info
				parent_object = HNComments.objects.get(id=comment_id)
				if(parent_object.cache + datetime.timedelta(minutes=cache_minutes) < timezone.now()):
					traverse_comment(story_soup.parent, parent_object.parent, parent_object.story_id, perma=True)
					parent_object = HNComments.objects.get(id=comment_id)
			except HNComments.DoesNotExist:
				# Since the comment doesn't exist we have to improvise with the data a bit
				# Story is is not provided for permalinked comments, but parent id is
				# Story id will therefore temporarely we set to the comment id
				traverse_comment(story_soup.parent, None, comment_id, perma=True)
				parent_object = HNComments.objects.get(id=comment_id)
			story_id = parent_object.story_id
			permalink = True
			story = False
		poll = False
		if story:
			# Poll
			if len(story_soup.parent.findAll('tr')) > 6:
				poll = True
				# I don't like using try here. Needs to be cleaned up
				try:
					poll_update(story['id'], story_soup.parent.findAll('tr')[5].findAll('td')[1])
					story['selfpost_text'] = html2markup(story_soup.parent.findAll('tr')[3].findAll('td')[1].decode_contents())
				except AttributeError:
					# No comment before poll
					poll_update(story['id'], story_soup.parent.findAll('tr')[3].findAll('td')[1])
					story['selfpost_text'] = ''
			# Check for self post text
			elif len(story_soup.parent.findAll('tr')) == 6:
				story['selfpost_text'] = html2markup(story_soup.parent.findAll('tr')[3].findAll('td')[1].decode_contents())
			else:
				story['selfpost_text'] = ''
			story_object = Stories(id=story['id'], title=story['title'],
							url=story['url'], score=story['score'], selfpost=story['selfpost'],
							selfpost_text=story['selfpost_text'], poll=poll, domain=story['domain'],
							username=story['username'],	comments=story['comments'], time=story['time'], cache=timezone.now())
			story_object.save()
		if story or permalink:
			# Updating cache
			comments_cache, created = HNCommentsCache.objects.get_or_create(pk=comment_id, defaults={'time': timezone.now})
			comments_cache.time = timezone.now()
			comments_cache.save()
			# If there is a poll there will be an extra table before comments
			if poll:
				i = 3
			else:
				i = 2
			comments_soup = soup.html.body.table.findAll('table')[i].findAll('table')
			# Traversing all top comments
			for comment_soup in comments_soup:
				td_default = comment_soup.tr.find('td', {'class': 'default'})
				# Converting indent to a more readable format (0, 1, 2...)
				indenting = int(td_default.previousSibling.previousSibling.img['width'], 10) / 40
				if indenting == 0:
					traverse_comment(comment_soup, parent_object, story_id)


def story_info(story_soup):
	if not story_soup.find('td'):
		return False
	title = story_soup.find('td', {'class': 'title'})
	# In some special cases there are more than one title class
	# Should probably make the initial query a bit more strict
	if story_soup.findAll('td')[0] == title:
		title = story_soup.findAll('td', {'class': 'title'})[1]
	subtext = story_soup.findNext('tr').find('td', {'class': 'subtext'})
	if subtext.findAll("a"):
		# Turns out normal dicts aren't ordered
		story = OrderedDict()
		story['url'] = urllib2.unquote(title.find('a')['href'])
		story['title'] = title.find('a').decode_contents()
		try:
			story['selfpost'] = False
			story['domain'] = ''.join(title.find('span', {'class': 'comhead'}))
		except TypeError:
			# No domain provided, must be a Ask HN post
			story['selfpost'] = True
			story['domain'] = ''
			story['url'] = ''
		story['score'] = int(re.search(r'(\d+) points?', ''.join(subtext.find("span"))).group(1))
		story['username'] = ''.join(subtext.findAll("a")[0])
		# Don't ask me about the "discu" thing. It just works
		story['comments'] = ''.join(subtext.findAll("a")[1]).rstrip("discu").rstrip(" comments")
		if(story['comments'] == ""):
			story['comments'] = 0
		# Unfortunalely HN doesn't show any form timestamp other than "x hours"
		# meaning that the time scraped is only approximately correct.
		story['time'] = datetime.datetime(*p.parse(subtext.findAll("a")[1].previousSibling + ' ago')[0][:6]).replace(tzinfo=tz)
		# parsedatetime doesn't have any built in support for DST
		if time.localtime().tm_isdst:
			story['time'] = story['time'] + datetime.timedelta(hours=-1)
		story['id'] = re.search('item\?id\=(\d+)$', subtext.findAll("a")[1]['href']).group(1)
		return story
	else:
		return False


def traverse_comment(comment_soup, parent_object, story_id, perma=False):
	comment = OrderedDict()
	# Comment <td> container shortcut
	td_default = comment_soup.tr.find('td', {'class': 'default'})
	# Retrieving comment id from the permalink
	try:
		comment['id'] = int(re.search(r'item\?id=(\d+)$', td_default.findAll('a')[1]['href']).group(1), 10)
	except IndexError:
		return False
	comment['username'] = ''.join(td_default.find('a').findAll(text=True))
	# Get html contents of the comment excluding <span> and <font>
	comment['text'] = td_default.find('span', {'class': 'comment'}).font.decode_contents()
	# Simple hack for fixing troubles with urlize inside code tags
	# comment['text'] = re.sub(r'(</code>)', r' \1', comment['text'])

	comment['text'] = html2markup(comment['text'])
	hex_color = td_default.find('span', {'class': 'comment'}).font['color']
	# All colors are in the format of #XYXYXY, meaning that they are all grayscale.
	# Get percent by grabbing the red part of the color (#XY)
	comment['hiddenpercent'] = int(re.search(r'^#(\w{2})', hex_color).group(1), 16) / 2.5
	comment['hiddencolor'] = hex_color
	comment['time'] = datetime.datetime(*p.parse(td_default.find('a').nextSibling + ' ago')[0][:6]).replace(tzinfo=tz)
	# parsedatetime doesn't have any built in support for DST
	if time.localtime().tm_isdst == 1:
		comment['time'] = comment['time'] + datetime.timedelta(hours=-1)
	# Some extra trickery for permalinked comments
	if perma:
		parent_id = int(re.search(r'item\?id=(\d+)$', td_default.findAll('a')[2]['href']).group(1), 10)
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
	comment_object = HNComments(id=comment['id'], story_id=story_id, username=comment['username'],
								text=comment['text'], hiddenpercent=comment['hiddenpercent'],
								hiddencolor=comment['hiddencolor'], time=comment['time'], cache=timezone.now(), parent=parent_object)
	if perma and not parent_object and parent_id:
		# Forcing comment to be updated next time, since it doesn't have proper values
		cache = timezone.now() - datetime.timedelta(days=1)
		parent_object = HNComments(id=parent_id, username='', parent=None, cache=cache)
		parent_object.save()
		comment_object.parent = parent_object
	comment_object.save()
	# Traversing over child comments:
	# Since comments aren't actually children in the HTML we will have to parse all the siblings
	# and check if they have +1 indent indicating that they are a child.
	# However if a following comment has the same indent value it is not a child and neither a sub child meaning that all child comments
	# have been parsed.
	if not perma:
		indenting = int(td_default.previousSibling.previousSibling.img['width'], 10) / 40
		for sibling_soup in comment_soup.parent.parent.findNextSiblings('tr'):
			sibling_soup = sibling_soup.table
			# TODO: Check why this is needed for some comments
			if sibling_soup:
				sibling_td_default = sibling_soup.tr.find('td', {'class': 'default'})
				sibling_indenting = int(sibling_td_default.previousSibling.previousSibling.img['width'], 10) / 40
				if sibling_indenting == indenting + 1:
					traverse_comment(sibling_soup, comment_object, story_id)
				if sibling_indenting == indenting:
					break
	return True


def html2markup(comment):
	# Remove <a>
	comment = re.sub(r'<a href="(.*?)" rel="nofollow">.*?\s*?</a>', r' \1 ', comment)
	# comment = re.sub(r'\s*<i>\s*(.+)\s*</i>\s*', r' *\1* ', comment)
	comment = re.sub(r'</?i>', r'*', comment)
	# Change <p> to \n
	comment = re.sub(r'<p>', r'\n\n', comment)
	comment = re.sub(r'</p>', r'', comment)
	# Code blocks to just two spaces on a new line
	comment = re.sub(r'<pre><code>\s*', r'  ', comment)
	comment = re.sub(r'</code></pre>', r'', comment)
	# HTML Escape
	# comment = html.escape(comment)
	return comment


def poll_update(story_id, poll_soup):
	for poll_element in poll_soup.table.findAll('tr')[::3]:
		poll = {'name': poll_element.findAll('td')[1].div.font.decode_contents(),
				'score': int(re.search(r'(\d+) points?', poll_element.findNext('tr').findAll('td')[1].span.span.decode_contents()).group(1)),
				'id': poll_element.findNext('tr').findAll('td')[1].span.span['id'].lstrip('score_')
		}
		Poll(id=poll['id'], name=poll['name'], score=poll['score'], story_id=story_id).save()


def stories(page=1, limit=25, story_type=None, over_filter=0):
	now = timezone.now()
	stories = Stories.objects.all()
	# Only show the last week
	enddate = datetime.datetime.today().replace(tzinfo=tz)
	startdate = enddate - datetime.timedelta(days=7)
	stories = stories.filter(time__range=[startdate, enddate])
	if story_type:
		if story_type == 'best':
			stories = stories.order_by('-score')
		elif story_type == 'newest':
			stories = stories.order_by('-time')
		else:
			stories = stories.filter(story_type=story_type)
	if over_filter > 0:
		stories = stories.filter(score__gte=over_filter)
	if not story_type in ['newest', 'best']:
		# HN Sorting
		sorted_stories = []
		for story in stories:
			time_hours = (now - story.time).total_seconds() / 3600
			score = calculate_score(story.score, time_hours)
			temp = {'story': story, 'score': score}
			sorted_stories.append(temp)
		sorted_stories = sorted(sorted_stories, key=lambda story: story['score'], reverse=True)
		stories = [story['story'] for story in sorted_stories]
	paginator = Paginator(stories, limit)
	try:
		stories = paginator.page(page)
	except (InvalidPage, EmptyPage):
		stories = paginator.page(paginator.num_pages)
	return stories


def comments(story_id):
	return HNComments.objects.all().filter(story_id=story_id)


def calculate_score(votes, item_hour_age, gravity=1.8):
	# Hacker News Sorting
	# Taken from http://amix.dk/blog/post/19574
	return (votes - 1) / pow((item_hour_age + 2), gravity)
