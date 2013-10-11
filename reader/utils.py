from django.utils import html
from tzlocal import get_localzone
import datetime
import parsedatetime
import re


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


def markup2html(comment):
	new_comment = ''
	# For code blocks
	code = False
	prev_line = True
	lines = comment.split('\n')
	for index, line in enumerate(lines):
		if re.match(r'^$', line):
			if code:
				if not prev_line:
					new_comment += '\n'
			else:
				new_comment += '<p>'
			prev_line = line
			continue
		# Making sure * won't be part of urls
		html.TRAILING_PUNCTUATION += [u'.*', u'*']
		# Create urls
		try:
			line = html.urlize(line, 63, True)
		except ValueError:
			# Temporarily fix for https://code.djangoproject.com/ticket/19070
			pass
		prev_line = line
		new_line = line
		# Starting with double space means it's a code block
		code_block = re.search(r'^  ', new_line)
		if code_block:
			if not code:
				new_line = '<p><pre><code>' + new_line
				code = True
			else:
				new_line = '\n' + new_line
		else:
			# Replacing * with <i> or </i>
			start = True
			# Index offset
			j = 0
			asterisks = []
			# First getting all asterisk that should be replaced
			# * not followed by " rel= or </a> (basically * in links)
			for x in re.finditer(r'\*((?!</a>)(?!" rel=))', line):
				i = x.start(0)
				try:
					prev_char = line[i - 1: i]
				except IndexError:
					prev_char = None

				try:
					next_char = line[i + 1: i + 2]
				except IndexError:
					next_char = None

				prev_ws = re.match(r'\s', prev_char)
				next_ws = re.match(r'\s', next_char)
				# Replace all * with italic tag if it is either preceded or followed by another character
				# This means that ** is valid, but * * is not

				# The three steps check for the following:
				# "^*\S" or " *\S"
				# "\S*\S"
				# # "\S* " or "\S*$"
				# Which creates this in code:
				# 	if ((not prev_char or prev_ws) and not next_ws) or \
				# 		(prev_char and not prev_ws and (next_char and not next_ws)) or \
				# 		(prev_char and not prev_ws and (not next_char or next_ws)):
				# Shortened version of previous code
				if not next_ws or (prev_char and not prev_ws):
					asterisks.append(i)
			# Replace all found asterisks
			if len(asterisks) > 1:
				for i, asterisk in enumerate(asterisks):
					# If there is an odd number of asterisks leave the last one
					if (i + 1) == len(asterisks) and len(asterisks) % 2:
						continue
					if start:
						italic = '<i>'
					else:
						italic = '</i>'
					start = not start
					# Replacing in line with some offset corrections
					new_line = new_line[0: asterisk + j] + italic + new_line[asterisk + j + 1:]
					# Adding offset (string has more letters after adding <i>)
					j += len(italic) - 1
		if not code_block:
			if code:
				# Ending code tag
				new_line = '</code></pre></p>' + new_line
				code = False
			else:
				new_line += ' '
		# Append proper closing tags if line is last and in a code block
		if code and index == (len(lines) - 1):
			new_line += '</code></pre></p>'
		new_comment += new_line
	return new_comment


def calculate_score(votes, item_hour_age, gravity=1.8):
	# Hacker News Sorting
	# Taken from http://amix.dk/blog/post/19574
	return (votes - 1) / pow((item_hour_age + 2), gravity)


def parse_time(time_string):
	p = parsedatetime.Calendar()
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
