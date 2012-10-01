# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'HNComments.text'
        db.add_column('reader_hncomments', 'text',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'HNComments.hiddenpercent'
        db.add_column('reader_hncomments', 'hiddenpercent',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0, max_length=10),
                      keep_default=False)

        # Adding field 'HNComments.hiddencolor'
        db.add_column('reader_hncomments', 'hiddencolor',
                      self.gf('django.db.models.fields.CharField')(default='#000000', max_length=7),
                      keep_default=False)

        # Adding field 'HNComments.cache'
        db.add_column('reader_hncomments', 'cache',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)


        # Changing field 'HNComments.id'
        db.alter_column('reader_hncomments', 'id', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True))

    def backwards(self, orm):
        # Deleting field 'HNComments.text'
        db.delete_column('reader_hncomments', 'text')

        # Deleting field 'HNComments.hiddenpercent'
        db.delete_column('reader_hncomments', 'hiddenpercent')

        # Deleting field 'HNComments.hiddencolor'
        db.delete_column('reader_hncomments', 'hiddencolor')

        # Deleting field 'HNComments.cache'
        db.delete_column('reader_hncomments', 'cache')


        # Changing field 'HNComments.id'
        db.alter_column('reader_hncomments', 'id', self.gf('django.db.models.fields.AutoField')(primary_key=True))

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
            'text': ('django.db.models.fields.TextField', [], {'default': "''"}),
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