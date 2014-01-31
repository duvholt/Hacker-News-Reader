from bs4 import BeautifulSoup
from django.conf import settings
from middleware import get_request
import re
import requests
import utils


def comments(commentid):
	return read('item?id=' + unicode(commentid))


def stories(story_type, over_filter=None):
	if story_type == 'news' and isinstance(over_filter, int):
		return read('over?points=' + unicode(over_filter))
	elif story_type in ['best', 'active', 'newest', 'ask', 'news']:
		return read(story_type)


def userpage(username):
	return read('user?id=' + unicode(username))


def login():
	return read('login')


def read(url):
	try:
		headers = {'User-Agent': 'Hacker News Reader (' + settings.DOMAIN_URL + ')'}
		cookies = None
		request = get_request()
		if request and 'usercookie' in request.session:
			cookies = {'user': request.session['usercookie']}
		try:
			r = requests.get('https://news.ycombinator.com/' + url, headers=headers, cookies=cookies, timeout=10)
		except requests.exceptions.Timeout:
			raise utils.ShowAlert('Connection to news.ycombinator.com timed out')
		if re.match(r'^We\'ve limited requests for old items', r.text):
			raise utils.ShowAlert('Requests have been limited for old items. It might take a while before you can access this.')
		elif re.match(r'^We\'ve limited requests for this url', r.text):
			raise utils.ShowAlert('Requests have been limited for this page. It might take a while before you can access this.')
		elif re.match(r'^No such user.$', r.text):
			raise utils.ShowAlert('No such user.')
		elif re.match(r'^No such item.$', r.text):
			raise utils.ShowAlert('Item not found')
		elif re.match(r'^((?!<body>).)*$', r.text):
			raise utils.ShowAlert('Hacker News is either not working or parsing failed')
		elif re.match(r'<title>Error</title>', r.text):
			raise utils.ShowAlert('Hacker News is down')
	except requests.HTTPError:
		raise utils.ShowAlert('Could not connect to news.ycombinator.com, try again later.<br>\
			If this error persists please contact the developer.')
	return BeautifulSoup(r.text, from_encoding='utf-8')
