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
	line_number = 0
	new_comment = ''
	code = False
	for line in comment.split('\n'):
		# Code tags
		if re.search(r'^  .*$', line):
			if not code:
				line = '<p><pre><code>' + line
				code = True
		else:
			if code:
				line = '</code></pre></p>'
				code = False
			# Ensuring that there are more than two *
			if len(re.findall(r'\*', line)) > 1:
				# Replacing * with <i> or </i>
				# TODO: r'\**\*' replace first
				start = True
				# Index offset
				j = 0
				for x in re.finditer(r'\*', line):
					i = x.start(0)
					if line[i + 1] == " ":
						continue
					if start:
						start = False
						italic = '<i>'
					else:
						start = True
						italic = '</i>'
					line = line[0: i + j] + italic + line[i + j + 1:]
					# Adding offset (string has more letters after adding <i>)
					j += len(italic) - 1
		# urlize
		line = html.urlize(line, 63, True)
		# Adding <p>
		if line_number > 0:
			if not code:
				line = '<p>' + line + '</p>'
			else:
				line = line + '\n'
		new_comment += line
		line_number += 1
	return new_comment
markup2html.is_safe = True
