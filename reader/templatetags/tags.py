from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.simple_tag
def active(request, pattern):
	import re
	if re.search(pattern, request.path):
		return 'active'
	return ''


@register.filter
@stringfilter
def upto(value, delimiter=None):
	return value.split(delimiter)[0]
upto.is_safe = True
