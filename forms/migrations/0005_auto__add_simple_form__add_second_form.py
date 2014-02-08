# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'simple_form'
        db.create_table(u'forms_simple_form', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=300)),
            ('age', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal(u'forms', ['simple_form'])

        # Adding model 'second_form'
        db.create_table(u'forms_second_form', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=300)),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forms.simple_form'])),
        ))
        db.send_create_signal(u'forms', ['second_form'])


    def backwards(self, orm):
        # Deleting model 'simple_form'
        db.delete_table(u'forms_simple_form')

        # Deleting model 'second_form'
        db.delete_table(u'forms_second_form')


    models = {
        u'forms.second_form': {
            'Meta': {'object_name': 'second_form'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forms.simple_form']"}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'})
        },
        u'forms.simple_form': {
            'Meta': {'object_name': 'simple_form'},
            'age': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'})
        }
    }

    complete_apps = ['forms']