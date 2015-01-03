# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HNComments',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('story_id', models.PositiveIntegerField(default=0, max_length=10, null=True)),
                ('username', models.CharField(max_length=150)),
                ('text', models.TextField(default=b'')),
                ('hiddenpercent', models.PositiveIntegerField(default=0, max_length=10)),
                ('hiddencolor', models.CharField(default=b'#000000', max_length=7)),
                ('time', models.DateTimeField(null=True)),
                ('cache', models.DateTimeField(null=True)),
                ('dead', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(related_name='children', to='reader.HNComments', null=True)),
            ],
            options={
                'ordering': ['dead', 'cache'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HNCommentsCache',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=1000)),
                ('score', models.PositiveIntegerField(max_length=5)),
                ('story_id', models.PositiveIntegerField(default=0, max_length=10, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stories',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=2083)),
                ('selfpost', models.BooleanField(default=False)),
                ('selfpost_text', models.TextField(default=b'', null=True)),
                ('poll', models.BooleanField(default=False)),
                ('dead', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=150, null=True)),
                ('score', models.PositiveIntegerField(max_length=5)),
                ('comments', models.PositiveIntegerField(max_length=5)),
                ('story_type', models.CharField(default=b'news', max_length=30)),
                ('time', models.DateTimeField()),
                ('cache', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('time', models.DateTimeField(null=True)),
                ('over', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('username', models.CharField(max_length=150, serialize=False, primary_key=True)),
                ('created', models.DateTimeField()),
                ('karma', models.IntegerField(default=1, null=True)),
                ('avg', models.DecimalField(default=b'', null=True, max_digits=20, decimal_places=2)),
                ('about', models.TextField(default=b'', null=True)),
                ('cache', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
