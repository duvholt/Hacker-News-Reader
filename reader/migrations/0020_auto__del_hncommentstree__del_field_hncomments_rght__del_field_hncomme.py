# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'HNCommentsTree'
        db.delete_table(u'reader_hncommentstree')

        # Deleting field 'HNComments.rght'
        db.delete_column(u'reader_hncomments', u'rght')

        # Deleting field 'HNComments.tree_id'
        db.delete_column(u'reader_hncomments', u'tree_id')

        # Deleting field 'HNComments.lft'
        db.delete_column(u'reader_hncomments', u'lft')

        # Deleting field 'HNComments.level'
        db.delete_column(u'reader_hncomments', u'level')


        # Changing field 'HNComments.parent'
        db.alter_column(u'reader_hncomments', 'parent_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['reader.HNComments']))

    def backwards(self, orm):
        # Adding model 'HNCommentsTree'
        db.create_table(u'reader_hncommentstree', (
            ('username', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['reader.HNCommentsTree'])),
            ('text', self.gf('django.db.models.fields.TextField')(default='')),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('dead', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('id', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('hiddenpercent', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, max_length=10)),
            ('rgt', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('story_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, max_length=10, null=True)),
            ('cache', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('hiddencolor', self.gf('django.db.models.fields.CharField')(default='#000000', max_length=7)),
            ('depth', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'reader', ['HNCommentsTree'])

        # Adding field 'HNComments.rght'
        db.add_column(u'reader_hncomments', u'rght',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'HNComments.tree_id'
        db.add_column(u'reader_hncomments', u'tree_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'HNComments.lft'
        db.add_column(u'reader_hncomments', u'lft',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'HNComments.level'
        db.add_column(u'reader_hncomments', u'level',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True),
                      keep_default=False)


        # Changing field 'HNComments.parent'
        db.alter_column(u'reader_hncomments', 'parent_id', self.gf('mptt.fields.TreeForeignKey')(null=True, to=orm['reader.HNComments']))

    models = {
        u'reader.hncomments': {
            'Meta': {'object_name': 'HNComments'},
            'cache': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'dead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hiddencolor': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '7'}),
            'hiddenpercent': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '10'}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['reader.HNComments']"}),
            'story_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '10', 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'reader.hncommentscache': {
            'Meta': {'object_name': 'HNCommentsCache'},
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'reader.poll': {
            'Meta': {'object_name': 'Poll'},
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5'}),
            'story_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '10', 'null': 'True'})
        },
        u'reader.stories': {
            'Meta': {'object_name': 'Stories'},
            'cache': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5'}),
            'dead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5'}),
            'selfpost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'selfpost_text': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'story_type': ('django.db.models.fields.CharField', [], {'default': "'news'", 'max_length': '30'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2083'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'})
        },
        u'reader.storycache': {
            'Meta': {'object_name': 'StoryCache'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'over': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'reader.userinfo': {
            'Meta': {'object_name': 'UserInfo'},
            'about': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'avg': ('django.db.models.fields.DecimalField', [], {'default': "''", 'null': 'True', 'max_digits': '20', 'decimal_places': '2'}),
            'cache': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'karma': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '150', 'primary_key': 'True'})
        }
    }

    complete_apps = ['reader']