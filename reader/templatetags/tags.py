from django import template
from django.template.defaultfilters import stringfilter
import re
from django.core.urlresolvers import reverse
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
	if re.search(r'over', request.path) and re.search(r'over/(\d+)', request.path).group(1) == number:
		return 'active'
	elif number == '0' and not re.search(r'over', request.path):
		return 'active'
	return ''
