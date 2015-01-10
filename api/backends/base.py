from abc import ABCMeta, abstractmethod
from django.conf import settings
from django.utils import timezone
from reader import models, utils
import datetime
import requests


class CouldNotParse(Exception):
    """Generic exception when parsing fails"""
    pass


class BaseAPI(object):
    """Base class for API backends"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def stories(self):
        """Retrieving stories"""
        pass

    @abstractmethod
    def comments(self):
        """Retrieving comments"""
        pass

    @abstractmethod
    def userpage(self):
        """Retrieving userpage"""
        pass

    def parent(self, parent_id):
        """Finds parent or creates a dummy parent if not found"""
        try:
            # Checking if the parent object is in the db
            parent_object = models.HNComments.objects.get(pk=parent_id)
            # Update story_id if unknown
        except models.HNComments.DoesNotExist:
            # Forcing comment to be updated next time, since it doesn't have proper values
            cache = timezone.now() - datetime.timedelta(days=10)
            parent_object = models.HNComments(id=parent_id, username='', parent=None, cache=cache)
            parent_object.save()
            # story_id is at this moment actually comment id of the parent object.
            # Trying to correct this by checking for actualy story_id in the db
            # ^ WRONG
            # ^ Brilliant commenting...
        if not self.story_id:
            if parent_object.story_id:
                self.story_id = parent_object.story_id
            else:
                self.story_id = self.itemid
        return parent_object


class BaseFetch(object):
    items = None
    users = None
    ext = ''

    def __init__(self):
        self.session = requests.Session()

    def querystring(self, dictionary):
        """
        Converts a dictionary to a querystring
        {'key1': 1, 'key2': 2} -> ?key1=1&key2=2
        """
        return '?' + '&'.join([k + '=' + v for k, v in dictionary.items()])

    @abstractmethod
    def stories(self, filters, by_date=False):
        pass

    def comments(self, id):
        return self.fetch(self.items + str(id))

    def userpage(self, username):
        return self.fetch(self.users + username)

    def fetch(self, url, ext=True):
        if ext:
            url += self.ext
        headers = {'User-Agent': 'Hacker News Reader (' + settings.DOMAIN_URL + ')'}
        try:
            r = self.session.get(url, headers=headers, timeout=5)
        except(requests.exceptions.Timeout, requests.exceptions.SSLError) as e:
            raise utils.ShowAlert('Connection timed out')
        try:
            return r.json()
        except ValueError:
            raise utils.ShowAlert("Failed to fetch item")
