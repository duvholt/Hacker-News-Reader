# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Stories'
        db.create_table('reader_stories', (
            ('id', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=2083)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('score', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=5)),
            ('comments', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=5)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('cache', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('reader', ['Stories'])

        # Adding model 'HNComments'
        db.create_table('reader_hncomments', (
            ('id', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('story_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, max_length=10)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('text', self.gf('django.db.models.fields.TextField')(default='')),
            ('hiddenpercent', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, max_length=10)),
            ('hiddencolor', self.gf('django.db.models.fields.CharField')(default='#000000', max_length=7)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('cache', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['reader.HNComments'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('reader', ['HNComments'])


    def backwards(self, orm):
        # Deleting model 'Stories'
        db.delete_table('reader_stories')

        # Deleting model 'HNComments'
        db.delete_table('reader_hncomments')


    models = {
        'reader.hncomments': {
            'Meta': {'object_name': 'HNComments'},
            'cache': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'hiddencolor': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '7'}),
            'hiddenpercent': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '10'}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['reader.HNComments']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'story_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '10'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'reader.stories': {
            'Meta': {'object_name': 'Stories'},
            'cache': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2083'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'})
        }
    }

    complete_apps = ['reader']