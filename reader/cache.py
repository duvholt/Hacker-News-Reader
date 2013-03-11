from django.utils import timezone
import parsedatetime.parsedatetime as pdt
# import parsedatetime.parsedatetime_consts as pdc
import datetime
from reader.models import Stories, HNComments, StoryCache, HNCommentsCache
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from tzlocal import get_localzone
import reader.utils as utils
import reader.hnparse as hnparse


# c = pdc.Constants()
p = pdt.Calendar()
tz = get_localzone()


def update_stories(cache_minutes=20, story_type='news', over_filter=0):
	try:
		if story_type == 'over':
			# Over points can have different values meaning that it can't be cached normal
			cachetime = StoryCache.objects.get(name=story_type, over=over_filter).time
		else:
			cachetime = StoryCache.objects.get(name=story_type).time
	except StoryCache.DoesNotExist:
		# Force updating cache
		cachetime = timezone.now() - datetime.timedelta(days=1)
	# More than cache_minutes since cache was updated
	if(cachetime + datetime.timedelta(minutes=cache_minutes) < timezone.now()):
		hnparse.stories(story_type=story_type, over_filter=over_filter)


def update_comments(commentid, cache_minutes=20):
	try:
		cachetime = HNCommentsCache.objects.get(pk=commentid).time
	except HNCommentsCache.DoesNotExist:
		# Force updating cache
		cachetime = timezone.now() - datetime.timedelta(days=1)
	if(cachetime + datetime.timedelta(minutes=cache_minutes) < timezone.now()):
		hnparse.comments(commentid=commentid, cache_minutes=cache_minutes)


def stories(page=1, limit=25, story_type=None, over_filter=0):
	now = timezone.now()
	stories = Stories.objects.all()
	# Only show the last week
	enddate = datetime.datetime.today().replace(tzinfo=tz)
	startdate = enddate - datetime.timedelta(days=7)
	stories = stories.filter(time__range=[startdate, enddate])
	if story_type:
		if story_type == 'best':
			stories = stories.order_by('-score')
		elif story_type == 'newest':
			stories = stories.order_by('-time')
		else:
			stories = stories.filter(story_type=story_type)
	if over_filter > 0:
		stories = stories.filter(score__gte=over_filter)
	if not story_type in ['newest', 'best']:
		# HN Sorting
		sorted_stories = []
		for story in stories:
			time_hours = (now - story.time).total_seconds() / 3600
			score = utils.calculate_score(story.score, time_hours)
			sorted_stories.append({'story': story, 'score': score})
		sorted_stories = sorted(sorted_stories, key=lambda story: story['score'], reverse=True)
		stories = [story['story'] for story in sorted_stories]
	paginator = Paginator(stories, limit)
	try:
		stories = paginator.page(page)
	except (InvalidPage, EmptyPage):
		stories = paginator.page(paginator.num_pages)
	return stories


def comments(story_id):
	return HNComments.objects.all().filter(story_id=story_id)
