import re
import datetime
import parsedatetime.parsedatetime as pdt
from tzlocal import get_localzone


class UserMessage():
# Taken from http://www.djangocurrent.com/2011/04/django-pattern-for-reporting.html
	def __init__(self, title="", text=[], url=None):
		self.title = title
		self.text = text if hasattr(text, '__iter__') else [text]
		self.url = url


class ShowAlert(Exception):
	def __init__(self, message, level='error'):
		self.message = message
		self.level = level


class OldItemDenied(Exception):
	pass


class UrlDenied(Exception):
	pass


class ParsingError(Exception):
	pass


def html2markup(comment):
	# Remove <a>
	comment = re.sub(r'<a href="(.+?)" rel="nofollow">.+?</a>', r'\1', comment)
	# Change <i> to *
	comment = re.sub(r'</?i>', r'*', comment)
	# Change <p> to \n
	comment = re.sub(r'<p>', r'\n\n', comment)
	comment = re.sub(r'</p>', r'', comment)
	# Code blocks to just two spaces on a new line
	comment = re.sub(r'<pre><code>\s{2}', r'  ', comment)
	comment = re.sub(r'</code></pre>', r'', comment)
	return comment


def calculate_score(votes, item_hour_age, gravity=1.8):
	# Hacker News Sorting
	# Taken from http://amix.dk/blog/post/19574
	return (votes - 1) / pow((item_hour_age + 2), gravity)


def parse_time(time_string):
	p = pdt.Calendar()
	tz = get_localzone()
	return datetime.datetime(*p.parse(time_string)[0][:6]).replace(tzinfo=tz)


def poll_percentage(number, total, rounding=2):
	rounding = int(rounding)
	if total != 0:
		return round((float(number) / float(total)) * 100, rounding)
	else:
		return 0.0

def domain(url):
	return re.findall(r'^(?:.+//)?(?:www\.)?([^/#?]*)', url)[0].lower()