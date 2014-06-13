from abc import ABCMeta, abstractmethod
from django.utils import timezone
from reader import models
import datetime


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
        if not self.story_id:
            if parent_object.story_id:
                self.story_id = parent_object.story_id
            else:
                self.story_id = self.itemid
        return parent_object
