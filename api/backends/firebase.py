from .base import BaseAPI, BaseFetch
from django.utils import timezone
from reader import models
from reader import utils
from tzlocal import get_localzone
import datetime
import pytz
import time


class FirebaseAPI(BaseAPI):
    def __init__(self):
        self.fetch = FirebaseFetch()

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
        filters['hitsPerPage'] = '100'
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
                # story_object.cache = timezone.now()
                story_object.save()

    def comments(self, itemid, cache_minutes):
        self.itemid = itemid
        comments = self.fetch.comments(self.itemid)
        if comments['type'] in ['story', 'poll']:
            self.story_id = self.itemid
            self.story_info(comments)
            count = 0
            for comment_id in comments['kids']:
                count += 1
                comment = self.fetch.comments(comment_id)
                count += self.traverse_comments(comment)
            self.story.comments = count
            if comments['type'] == 'poll':
                self.story.poll = True
                self.poll_info(comments['parts'])
            self.story.save()
            # models.HNCommentsCache(id=self.itemid, time=timezone.now()).save()
        elif comments['type'] == 'comment':
            self.story = None
            try:
                comment_object = models.HNComments.objects.get(id=self.itemid)
                self.story_id = comment_object.story_id
            except models.HNComments.DoesNotExist:
                self.story_id = None
            if self.story_id:
                try:
                    self.story = models.Stories.objects.get(id=self.story_id)
                except models.Stories.DoesNotExist:
                    pass
            self.traverse_comments(comments, None)
            # models.HNCommentsCache(id=self.itemid, time=timezone.now()).save()
        elif comments['type'] == 'pollopt':
            raise utils.ShowAlert('Item is a poll option', level='info')

    def traverse_comments(self, comment, parent_object=None):
        if not parent_object and not self.story:
            parent_object = self.parent(comment['parent'])
        HNComment = models.HNComments()
        if 'deleted' in comment:
            return 0
        if 'dead' in comment:
            HNComment.dead = comment['dead']
        HNComment.id = comment['id']
        HNComment.username = comment['by']
        HNComment.text = utils.html2markup(comment['text'])
        HNComment.story_id = self.story_id
        HNComment.parent = parent_object
        tz = get_localzone()
        HNComment.time = self.dateformat(comment['time'])
        HNComment.cache = timezone.now()
        HNComment.save()
        # models.HNCommentsCache(id=HNComment.id, time=timezone.now()).save()
        count = 0
        if 'kids' in comment:
            for comment_id in comment['kids']:
                count += 1
                comment_child = self.fetch.comments(comment_id)
                count += self.traverse_comments(comment_child, HNComment)
        return count

    def story_info(self, story):
        self.story = models.Stories()
        self.story.id = self.story_id
        self.story.cache = timezone.now()
        self.story.title = story['title']
        if story['text']:
            self.story.selfpost = True
            self.story.selfpost_text = utils.html2markup(story['text'])
        self.story.username = story['by']
        self.story.url = "" if 'url' not in story else story['url']
        self.story.time = self.dateformat(story['time'])
        self.story.score = story['score']

    def poll_info(self, polls):
        for part in polls:
            part = self.fetch.comments(part)
            poll = models.Poll(id=part['id'])
            poll.time = self.dateformat(part['time'])
            poll.name = utils.html2markup(part['text'])
            poll.score = part['score']
            poll.story_id = part['parent']
            poll.save()

    def userpage(self, username):
        userpage = self.fetch.userpage(username)
        if not userpage:
            # User doesn't e
            return
        user = models.UserInfo()
        user.username = userpage['id']
        user.created = self.dateformat(userpage['created'])
        user.karma = userpage['karma']
        # user.avg = userpage['avg']
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
            return datetime.datetime.fromtimestamp(datecreate).replace(tzinfo=tz)


class FirebaseFetch(BaseFetch):
    items = 'https://hacker-news.firebaseio.com/v0/item/'
    users = 'https://hacker-news.firebaseio.com/v0/user/'
    ext = '.json'

    def stories(self, filters, by_date=False):
        pass
