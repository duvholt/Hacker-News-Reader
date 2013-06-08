from django import template
from django.template.defaultfilters import stringfilter
import re
from django.utils import html

register = template.Library()


@register.simple_tag
def active(request, pattern):
	if request and re.search(pattern, request.path):
		return 'active'
	return ''


@register.filter
@stringfilter
def upto(value, delimiter=None):
	return value.split(delimiter)[0]
upto.is_safe = True


@register.simple_tag
def create_url(request, number, prefix='page'):
	if re.search(r'(' + prefix + ')', request.path):
		reg = re.search(r'^/(.*)' + prefix + '/\d+(.*)$', request.path)
		return '/' + reg.group(1) + prefix + '/' + str(number) + reg.group(2)
	elif request.path == '/':
		return '/' + prefix + '/' + str(number)
	else:
		return re.search(r'(.*)$', request.path).group(1) + prefix + '/' + str(number)


@register.simple_tag
def active_limit(request, number):
	if request.COOKIES['stories_limit'] == number:
		return 'active'
	return ''


@register.simple_tag
def active_score(request, number):
	if request.GET.get('over') == number:
		return 'active'
	elif number == '0' and not request.GET.get('over'):
		return 'active'
	return ''


@register.simple_tag
def percentage(number, total, rounding=2):
	rounding = int(rounding)
	if total != 0:
		return round((float(number) / float(total)) * 100, rounding)
	else:
		return 0.0
	# return '{percent:.2%}'.format(percent=float(number) / float(total))


@register.filter
@stringfilter
def markup2html(comment):
	new_comment = ''
	# For code blocks
	code = False
	prev_line = True
	lines = comment.split('\n')
	paragraph = False
	for index, line in enumerate(lines):
		if re.match(r'^$', line):
			if code:
				if not prev_line:
					new_comment += '\n'
			else:
				new_comment += '<p>'
			prev_line = line
			continue
		# Create urls
		line = html.urlize(line, 63, True)
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


@register.filter(is_safe=False)
def lastobject(objects):
	try:
		return objects.reverse()[0]
	except IndexError:
		return ''


@register.filter(is_safe=False)
def lastpageobject(page):
	try:
		return page.object_list[-1]
	except AssertionError:
		return page.object_list[::-1][0]


@register.filter
def domain(url):
	return re.findall(r'^(?:.+//)?(?:www\.)?([^/#?]*)', url)[0].lower()
