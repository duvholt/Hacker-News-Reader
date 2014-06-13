from .base import BaseAPI
from django.conf import settings
from django.utils import timezone
from reader import models
from reader import utils
from tzlocal import get_localzone
import datetime
import pytz
import requests
import time


class AlgoliaAPI(BaseAPI):
    def __init__(self):
        self.fetch = AlgoliaFetch()

    def stories(self, story_type, over_filter=20):
        by_date = True
        if not over_filter:
            over_filter = 20
        filters = {}

        if story_type == 'best':
            filters['tags'] = '(story,poll)'
            by_date = False
        elif story_type == 'newest':
            filters['tags'] = '(story,poll)'
            over_filter = 0
        # elif story_type == 'self':
        #     filters['tags'] = '(story,poll)'
        elif story_type == 'show':
            filters['tags'] = 'show_hn'
            over_filter = 0
        elif story_type == 'ask':
            filters['tags'] = 'ask_hn'
            over_filter = 0
        elif story_type == 'poll':
            filters['tags'] = 'poll'
            over_filter = 0
        else:
            filters['tags'] = '(story,poll)'
        two_weeks_ago = datetime.datetime.now() - datetime.timedelta(days=14)
        filters['numericFilters'] = 'points%3E' + unicode(over_filter) + ',created_at_i%3E' + two_weeks_ago.strftime('%s')
        stories = self.fetch.stories(filters, by_date)
        if stories['nbHits'] > 0:
            for story in stories['hits']:
                story_object = models.Stories()
                story_object.time = self.dateformat(story['created_at'])
                story_object.title = story['title']
                story_object.username = story['author']
                story_object.score = story['points']
                story_object.id = story['objectID']
                story_object.comments = story['num_comments']
                if not story['url']:
                    story_object.url = ''
                else:
                    story_object.url = story['url']
                if story['story_text']:
                    story_object.selfpost = True
                    story_object.selfpost_text = story['story_text']
                if 'poll' in story['_tags']:
                    story_object.poll = True
                story_object.cache = timezone.now()
                story_object.save()

    def comments(self, itemid, cache_minutes):
        self.itemid = itemid
        comments = self.fetch.comments(self.itemid)
        if 'message' in comments:
            raise utils.ShowAlert(comments['message'])
        if comments['type'] in ['story', 'poll']:
            self.story_id = self.itemid
            self.story_info(comments)
            count = 0
            for comment in comments['children']:
                count += 1
                count += self.traverse_comments(comment)
            self.story.comments = count
            if comments['type'] == 'poll':
                self.story.poll = True
                self.poll_info(comments['options'])
            self.story.save()
            models.HNCommentsCache(id=self.itemid, time=timezone.now()).save()
        elif comments['type'] == 'comment':
            self.story = None
            try:
                comment_object = models.HNComments.objects.get(id=self.itemid)
                self.story_id = comment_object.story_id
            except models.HNComments.DoesNotExist:
                self.story_id = comments['story_id']
            if self.story_id:
                try:
                    self.story = models.Stories.objects.get(id=self.story_id)
                except models.Stories.DoesNotExist:
                    pass
            self.traverse_comments(comments, None)
            models.HNCommentsCache(id=self.itemid, time=timezone.now()).save()
        elif comments['type'] == 'pollopt':
            raise utils.ShowAlert('Item is a poll option', level='info')

    def traverse_comments(self, comment, parent_object=None):
        if not parent_object and not self.story:
            parent_object = self.parent(comment['parent_id'])
            print parent_object.id
        if 'author' not in comment:
            # Dead comment with no info
            return 0
        HNComment = models.HNComments()
        HNComment.id = comment['id']
        HNComment.username = comment['author']
        HNComment.text = utils.html2markup(comment['text'])
        HNComment.story_id = self.story_id
        HNComment.parent = parent_object
        tz = get_localzone()
        HNComment.time = self.dateformat(comment['created_at'])
        HNComment.cache = timezone.now()
        HNComment.save()
        models.HNCommentsCache(id=HNComment.id, time=timezone.now()).save()
        count = 0
        for comment_child in comment['children']:
            count += 1
            count += self.traverse_comments(comment_child, HNComment)
        return count

    def story_info(self, story):
        self.story = models.Stories()
        self.story.id = self.story_id
        self.story.title = story['title']
        if 'text' in story:
            self.story.selfpost = True
            self.story.selfpost_text = utils.html2markup(story['text'])
        self.story.username = story['author']
        self.story.url = "" if story['url'] is None else story['url']
        self.story.time = self.dateformat(story['created_at'])
        self.story.score = story['points']

    def poll_info(self, polls):
        for option in polls:
            poll = models.Poll(id=option['id'])
            poll.time = self.dateformat(option['created_at_i'])
            poll.name = utils.html2markup(option['text'])
            poll.score = option['points']
            poll.story_id = option['parent_id']
            poll.save()

    def userpage(self, username):
        userpage = self.fetch.userpage(username)
        user = models.UserInfo()
        if 'message' in userpage:
            raise utils.ShowAlert(userpage['message'])
        user.username = userpage['username']
        user.created = self.dateformat(userpage['created_at'])
        user.karma = userpage['karma']
        user.avg = userpage['avg']
        if userpage['about']:
            user.about = utils.html2markup(userpage['about'])
        else:
            user.about = None
        user.cache = timezone.now()
        user.save()

    @staticmethod
    def dateformat(datecreate):
        tz = pytz.utc
        # Date formatted as string
        if type(datecreate) is unicode:
            return datetime.datetime(*time.strptime(datecreate, '%Y-%m-%dT%H:%M:%S.000Z')[0:6], tzinfo=tz)
        # Unix time
        elif type(datecreate) is int:
            return datetime.datetime.fromtimestamp(datecreate)


class AlgoliaFetch(object):
    items = 'http://hn.algolia.com/api/v1/items/'
    users = 'http://hn.algolia.com/api/v1/users/'
    search = 'http://hn.algolia.com/api/v1/search'
    search_by_date = 'http://hn.algolia.com/api/v1/search_by_date'

    def stories(self, filters, by_date=False):
        # Dict to querystring
        querystring = '?' + '&'.join([k + '=' + v for k, v in filters.items()])
        if by_date:
            return self.fetch(self.search_by_date + querystring)
        else:
            return self.fetch(self.search + querystring)

    def comments(self, id):
        return self.fetch(self.items + str(id))

    def userpage(self, username):
        return self.fetch(self.users + username)

    def fetch(self, url):
        print url
        headers = {'User-Agent': 'Hacker News Reader (' + settings.DOMAIN_URL + ')'}
        r = requests.get(url, headers=headers, timeout=5)
        try:
            return r.json()
        except ValueError:
            raise utils.ShowAlert("Failed to fetch item")
