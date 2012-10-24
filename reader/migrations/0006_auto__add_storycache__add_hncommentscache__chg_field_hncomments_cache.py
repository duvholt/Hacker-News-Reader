# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StoryCache'
        db.create_table('reader_storycache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('reader', ['StoryCache'])

        # Adding model 'HNCommentsCache'
        db.create_table('reader_hncommentscache', (
            ('id', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('reader', ['HNCommentsCache'])


        # Changing field 'HNComments.cache'
        db.alter_column('reader_hncomments', 'cache', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):
        # Deleting model 'StoryCache'
        db.delete_table('reader_storycache')

        # Deleting model 'HNCommentsCache'
        db.delete_table('reader_hncommentscache')


        # Changing field 'HNComments.cache'
        db.alter_column('reader_hncomments', 'cache', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True))

    models = {
        'reader.hncomments': {
            'Meta': {'object_name': 'HNComments'},
            'cache': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'hiddencolor': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '7'}),
            'hiddenpercent': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '10'}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['reader.HNComments']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'story_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '10', 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'reader.hncommentscache': {
            'Meta': {'object_name': 'HNCommentsCache'},
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'reader.stories': {
            'Meta': {'object_name': 'Stories'},
            'cache': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5'}),
            'selfpost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'selfpost_text': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2083'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'})
        },
        'reader.storycache': {
            'Meta': {'object_name': 'StoryCache'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['reader']