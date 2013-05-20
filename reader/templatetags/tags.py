from django import template
from django.template.defaultfilters import stringfilter
import re
from django.utils import html

register = template.Library()


@register.simple_tag
def active(request, pattern):
	if re.search(pattern, request.path):
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
	return round((float(number) / float(total)) * 100, rounding)
	# return '{percent:.2%}'.format(percent=float(number) / float(total))


@register.filter
@stringfilter
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
			prev_line = line
			continue
		prev_line = line
		# Starting with double space means it's a code block
		code_block = re.search(r'^  ', line)
		if code_block:
			if not code:
				line = '<p><pre><code>' + line
				code = True
			else:
				line = '\n\n' + line
		else:
			# Replacing * with <i> or </i>
			asterisk_total = len(re.findall(r'\*', line))
			# Making sure that there are more than two *
			if asterisk_total > 1:
				start = True
				# Index offset
				j = 0
				for asterisk_count, x in enumerate(re.finditer(r'\*', line)):
					i = x.start(0)
					try:
						prev = line[i-1: i]
					except IndexError:
						prev = None

					try:
						next = line[i+1: i+2]
					except IndexError:
						next = None

					prev_ws = re.match(r'\s', prev)
					next_ws = re.match(r'\s', next)
					# Kinda messy, but the code tries to emulate HNs parsing
					# Replace all * with italic tag if it is either preceded or followed by another character
					# This means that ** is valid, but * * is not
					if ((not prev or prev_ws) and not next_ws) or \
						((prev and not prev_ws) and (next and not next_ws)) or \
						((prev and not prev_ws) and (not next or next_ws)):
						# If there is an odd number of asterisks leave the last one
						if asterisk_count == asterisk_total and asterisk_total % 2:
							continue
						if start:
							italic = '<i>'
						else:
							italic = '</i>'
						start = not start
						# Replacing in line with some offset corrections
						line = line[0: i + j] + italic + line[i + j + 1:]
						# Adding offset (string has more letters after adding <i>)
						j += len(italic) - 1
		# Create urls
		line = html.urlize(line, 63, True)
		if not code_block:
			# Adding <p>
			line = '<p>' + line + '</p>'
			# Ending code tag
			if code:
				line = '</code></pre></p>' + line
				code = False
		# Append proper closing tags if line is last and in a code block
		if code and index == (len(lines) - 1):
			line += '</code></pre></p>'
		new_comment += line
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
