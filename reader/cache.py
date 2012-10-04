from bs4 import BeautifulSoup
import urllib2
from django.utils import timezone
import parsedatetime.parsedatetime as pdt
import parsedatetime.parsedatetime_consts as pdc
import datetime
import pytz
import re
from reader.models import Stories, HNComments
import operator
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils import html
from collections import OrderedDict
import random
import time

now = timezone.now()
c = pdc.Constants()
p = pdt.Calendar(c)
norway = pytz.timezone('Europe/Oslo')


def update_stories(cache_time=20):
	try:
		cache = Stories.objects.latest('cache').cache
	except Stories.DoesNotExist:
		cache = now - datetime.timedelta(days=1)  # Force updating cache
	if(cache + datetime.timedelta(minutes=cache_time) < now):
		doc = urllib2.urlopen('http://news.ycombinator.com/').read()
		soup = BeautifulSoup(''.join(doc))
		stories_soup = soup.html.body.table.findAll('table')[1].findAll("tr")[::3]
		for story_soup in stories_soup:
			story = story_info(story_soup)
			story_object = Stories(id=story['id'], title=story['title'],
							url=story['url'], score=story['score'], domain=story['domain'],
							username=story['username'], comments=story['comments'], time=story['time'], cache=now)
			story_object.save()


def update_comments(story_id, cache_time=20, html_escape=False):
	try:
		cache = HNComments.objects.filter(story_id=story_id)[0].cache
	except IndexError:
		cache = now - datetime.timedelta(days=1)
	if(cache + datetime.timedelta(minutes=cache_time) < now):
		doc = urllib2.urlopen('https://news.ycombinator.com/item?id=' + str(story_id))
		soup = BeautifulSoup(''.join(doc))
		comments_soup = soup.html.body.table.findAll('table')[2].findAll('table')
		for comment_soup in comments_soup:
			td_default = comment_soup.tr.find('td', {'class': 'default'})
			indenting = int(td_default.previousSibling.previousSibling.img['width'], 10) / 40
			if indenting == 0:
				traverse_comment(comment_soup, None, story_id, html_escape)


def story_info(story_soup):
	i = 0
	if(story_soup.findAll('td')[0] == story_soup.find('td', {'class': 'title'})):
		i += 1
	subtext = story_soup.find('td', {'class': 'subtext'})
	if(subtext.findAll("a")):
		
	# story_soup = story_soup.findAll('td', {"class": "title"})
	# if story_soup:
	# 	subtext = story_soup[1].findNext('tr').find("td", {"class": "subtext"})
	# 	if(subtext.findAll("a")):
	# 		story = OrderedDict()
	# 		story['url'] = urllib2.unquote(story_soup[1].find('a')['href'])
	# 		story['title'] = ''.join(story_soup[1].find('a'))
	# 		story['score'] = ''.join(subtext.find("span")).rstrip(" points")
	# 		story['username'] = ''.join(subtext.findAll("a")[0])
	# 		story['comments'] = ''.join(subtext.findAll("a")[1]).rstrip("discu").rstrip(" comments")
	# 		if(story['comments'] == ""):
	# 			story['comments'] = 0
	# 		story['domain'] = ''.join(story_soup[1].find('a').findNext('span'))
	# 		story['time'] = datetime.datetime(*p.parse(subtext.findAll("a")[1].previousSibling + ' ago')[0][:6]).replace(tzinfo=norway)
	# 		# This might be incorrect, but it doesn't seem like parsedatetime supports DST
	# 		if time.localtime().tm_isdst == 1:
	# 			story['time'] = story['time'] + datetime.timedelta(hours=-1)
	# 		story['id'] = re.search('item\?id\=(\d+)$', subtext.findAll("a")[1]['href']).group(1)
	return story

def traverse_comment(comment_soup, parent_object, story_id, html_escape=False):

		comment = OrderedDict()
		# Comment <td> container shortcut
		td_default = comment_soup.tr.find('td', {'class': 'default'})
		# Retrieving comment id from the reply id
		try:
			comment['id'] = int(re.search(r'item\?id=(\d+)$', td_default.findAll('a')[1]['href']).group(1), 10)
		except IndexError:
			return False
		comment['username'] = ''.join(td_default.find('a').findAll(text=True))
		# Get html contents of the comment excluding <span> and <font>
		comment['text'] = ''.join([unicode(x) for x in td_default.find('span', {'class': 'comment'}).font])
		# Remove <a>
		comment['text'] = re.sub(r'<a href="(.*?)" rel="nofollow">.*?\s*?</a>', r' \1 ', comment['text'])
		# Remove <code>, it is not needed inside <pre>
		# comment['text'] = re.sub(r'\s*<code>\s*(.*)\s*[</code>]?\s*', r'  \1', comment['text'], flags=re.DOTALL)  # Bug here
		# Not sure if I am going to use HTML Escaping for Android yet
		if html_escape:
			# Convert <i> to *
			comment['text'] = re.sub(r'\s*<i>\s*(.+)\s*</i>\s*', r' *\1* ', comment['text'])
			# HTML Escape
			comment['text'] = html.escape(comment['text'])
		hex_color = td_default.find('span', {'class': 'comment'}).font['color']
		# All colors are in the format of #XYXYXY, meaning that they are all grayscale.
		# Get percent by grabbing the red part of the color (#XY), converting to int and dividing by (250/100)
		comment['hiddenpercent'] = int(re.search(r'^#(\w{2})', hex_color).group(1), 16) / 2.5
		comment['hiddencolor'] = hex_color
		comment['time'] = datetime.datetime(*p.parse(td_default.find('a').nextSibling + ' ago')[0][:6]).replace(tzinfo=norway)
		if time.localtime().tm_isdst == 1:
			comment['time'] = comment['time'] + datetime.timedelta(hours=-1)
		indenting = int(td_default.previousSibling.previousSibling.img['width'], 10) / 40
		comment_object = HNComments(id=comment['id'], story_id=story_id, username=comment['username'],
									text=comment['text'], hiddenpercent=comment['hiddenpercent'],
									hiddencolor=comment['hiddencolor'], time=comment['time'], cache=now, parent=parent_object)
		comment_object.save()
		# Traversing over child comments:
		# Since comments aren't actually children in the HTML we will have to parse all the siblings
		# and check if they have +1 indent indicating that they are a child.
		# However if a following comment has the same indent value it is not a child and neither a sub child meaning that all child comments
		# have been parsed.
		for sibling_soup in comment_soup.parent.parent.findNextSiblings('tr'):
			sibling_soup = sibling_soup.table
			# TODO: Check why this is needed for some comments
			if sibling_soup:
				sibling_td_default = sibling_soup.tr.find('td', {'class': 'default'})
				sibling_indenting = int(sibling_td_default.previousSibling.previousSibling.img['width'], 10) / 40
				if sibling_indenting == indenting + 1:
					traverse_comment(sibling_soup, comment_object, story_id, html_escape)
				if sibling_indenting == indenting:
					break
		return True


def stories(page=1, limit=20):
	stories = Stories.objects.all().filter(time__year=now.year, time__month=now.month, time__day=now.day).order_by('-score')
	stories = sorted(stories, key=operator.attrgetter('time'), reverse=True)
	paginator = Paginator(stories, limit)
	try:
		stories = paginator.page(page)
	except (InvalidPage, EmptyPage):
		stories = paginator.page(paginator.num_pages)
	return stories


def comments(story_id):
	return HNComments.objects.all().filter(story_id=story_id)
