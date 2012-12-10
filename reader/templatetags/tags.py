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
	lines = comment.split('\n\n')
	for index, line in enumerate(lines):
		code_r = re.search(r'^  ', line)
		# Code block tags
		if code_r:
			if not code:
				line = '<p><pre><code>' + line
				code = True
			else:
				line = '\n\n' + line
		else:
			# Ensuring that there are more than two *
			# TODO: There is a bug with ****. Low priority
			asterisk_total = len(re.findall(r'[^\s]\*|\*[^\s]', line))
			if asterisk_total > 1:
				asterisk_count = 0
				start = True
				# Index offset
				j = 0
				# Replacing * with <i> or </i>
				for x in re.finditer(r'[^\s]\*|\*[^\s]', line):
					asterisk_count += 1
					# If there is an odd number of asterisks leave the last one
					if asterisk_count == asterisk_total and asterisk_total % 2 is not 0:
						continue
					i = x.start(0)
					if re.search(r'[^\s]\*', x.group(0)):
						i += 1
					if start:
						italic = '<i>'
					else:
						italic = '</i>'
					start = not start
					line = line[0: i + j] + italic + line[i + j + 1:]
					# Adding offset (string has more letters after adding <i>)
					j += len(italic) - 1
		# Create urls
		line = html.urlize(line, 63, True)
		# Adding <p>
		if not code_r:
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
