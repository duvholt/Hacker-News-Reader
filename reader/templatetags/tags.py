from django import template
from django.template.defaultfilters import stringfilter
import re
import reader.utils as utils

register = template.Library()


@register.filter
def get_value(dict, key):
	return dict.get(key)


@register.simple_tag(takes_context=True)
def active(context, pattern):
	if re.search(pattern, context['request'].path):
		return 'active'
	return ''


@register.filter
@stringfilter
def upto(value, delimiter=None):
	return value.split(delimiter)[0]
upto.is_safe = True

@register.filter
def split(value, delimiter=None):
	return value.split(delimiter)


@register.simple_tag(takes_context=True)
def create_url(context, number, prefix='page'):
	path = context['request'].path
	if re.search(r'(' + prefix + ')', path):
		reg = re.search(r'^/(.*)' + prefix + '/\d+(.*)$', path)
		return '/' + reg.group(1) + prefix + '/' + str(number) + reg.group(2)
	elif path == '/':
		return '/' + prefix + '/' + str(number)
	else:
		return re.search(r'(.*)$', path).group(1) + prefix + '/' + str(number)


@register.simple_tag(takes_context=True)
def active_limit(context, number):
	if context['request'].COOKIES.get('stories_limit') == number:
		return 'selected'
	return ''


@register.simple_tag(takes_context=True)
def active_score(context, number):
	if context['request'].GET.get('over') == number:
		return 'selected'
	elif number == '0' and not context['request'].GET.get('over'):
		return 'selected'
	return ''


@register.simple_tag
def percentage(number, total, rounding=2):
	return utils.poll_percentage(number, total, rounding)


@register.filter
@stringfilter
def markup2html(comment):
	return utils.markup2html(comment)


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
	return utils.domain(url)
