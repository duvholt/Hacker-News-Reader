

# Taken from http://www.djangocurrent.com/2011/04/django-pattern-for-reporting.html
class UserMessage():
	def __init__(self, title="", text=[], url=None):
		self.title = title
		self.text = text if hasattr(text, '__iter__') else [text]
		self.url = url


class CustomError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
