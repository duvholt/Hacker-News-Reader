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
            ('score', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('comments', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('cache', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('reader', ['Stories'])

        # Adding model 'HNComments'
        db.create_table('reader_hncomments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=150)),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['reader.HNComments']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'reader.stories': {
            'Meta': {'object_name': 'Stories'},
            'cache': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2083'})
        }
    }

    complete_apps = ['reader']