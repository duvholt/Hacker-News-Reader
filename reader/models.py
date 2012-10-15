from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Stories(models.Model):
	id = models.PositiveIntegerField(primary_key=True)
	title = models.CharField(max_length=200)
	url = models.CharField(max_length=2083)
	selfpost = models.BooleanField(default=False)
	selfpost_text = models.TextField(default="", null=True)
	domain = models.CharField(max_length=200, null=True)
	username = models.CharField(max_length=150, null=True)
	score = models.PositiveIntegerField(max_length=5)
	comments = models.PositiveIntegerField(max_length=5)
	time = models.DateTimeField()
	cache = models.DateTimeField(auto_now_add=True, null=True)


class HNComments(MPTTModel):
	id = models.PositiveIntegerField(primary_key=True)
	story_id = models.PositiveIntegerField(max_length=10, default=0)
	username = models.CharField(max_length=150)
	text = models.TextField(default="")
	hiddenpercent = models.PositiveIntegerField(max_length=10, default=0)
	hiddencolor = models.CharField(max_length=7, default="#000000")
	time = models.DateTimeField(null=True)
	cache = models.DateTimeField(auto_now_add=True, null=True)
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

	class MPTTMeta:
		order_insertion_by = ['cache']  # lft gives None error
