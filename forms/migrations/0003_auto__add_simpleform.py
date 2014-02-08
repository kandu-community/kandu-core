# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'simpleForm'
        db.create_table(u'forms_simpleform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=300)),
            ('age', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal(u'forms', ['simpleForm'])


    def backwards(self, orm):
        # Deleting model 'simpleForm'
        db.delete_table(u'forms_simpleform')


    models = {
        u'forms.simpleform': {
            'Meta': {'object_name': 'simpleForm'},
            'age': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'})
        }
    }

    complete_apps = ['forms']