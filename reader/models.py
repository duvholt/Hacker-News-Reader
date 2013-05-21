from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Stories(models.Model):
	id = models.PositiveIntegerField(primary_key=True)
	title = models.CharField(max_length=200)
	url = models.CharField(max_length=2083)
	selfpost = models.BooleanField(default=False)
	selfpost_text = models.TextField(default="", null=True)
	poll = models.BooleanField(default=False)
	username = models.CharField(max_length=150, null=True)
	score = models.PositiveIntegerField(max_length=5)
	comments = models.PositiveIntegerField(max_length=5)
	story_type = models.CharField(max_length=30, default='news')
	time = models.DateTimeField()
	cache = models.DateTimeField(auto_now_add=True, null=True)


class HNComments(MPTTModel):
	id = models.PositiveIntegerField(primary_key=True)
	story_id = models.PositiveIntegerField(max_length=10, default=0, null=True)
	username = models.CharField(max_length=150)
	text = models.TextField(default="")
	hiddenpercent = models.PositiveIntegerField(max_length=10, default=0)
	hiddencolor = models.CharField(max_length=7, default="#000000")
	time = models.DateTimeField(null=True)
	cache = models.DateTimeField(null=True)
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
	dead = models.BooleanField(default=False)

	class MPTTMeta:
		order_insertion_by = ['cache']


class StoryCache(models.Model):
	name = models.CharField(max_length=30)
	time = models.DateTimeField(null=True)
	over = models.IntegerField(null=True)


class HNCommentsCache(models.Model):
	id = models.PositiveIntegerField(primary_key=True)
	time = models.DateTimeField(null=True, auto_now=True)


class UserInfo(models.Model):
	username = models.CharField(max_length=150, primary_key=True)
	created = models.DateTimeField()
	karma = models.IntegerField(null=True, default=1)
	avg = models.DecimalField(null=True, default="", max_digits=20, decimal_places=2)
	about = models.TextField(default="", null=True)
	cache = models.DateTimeField(auto_now_add=True, null=True)


class Poll(models.Model):
	id = models.PositiveIntegerField(primary_key=True)
	name = models.CharField(max_length=100)
	score = models.PositiveIntegerField(max_length=5)
	story_id = models.PositiveIntegerField(max_length=10, default=0, null=True)
