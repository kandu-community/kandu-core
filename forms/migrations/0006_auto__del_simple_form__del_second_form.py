# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'simple_form'
        db.delete_table(u'forms_simple_form')

        # Deleting model 'second_form'
        db.delete_table(u'forms_second_form')


    def backwards(self, orm):
        # Adding model 'simple_form'
        db.create_table(u'forms_simple_form', (
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('age', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=300)),
        ))
        db.send_create_signal(u'forms', ['simple_form'])

        # Adding model 'second_form'
        db.create_table(u'forms_second_form', (
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forms.simple_form'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=300)),
        ))
        db.send_create_signal(u'forms', ['second_form'])


    models = {
        
    }

    complete_apps = ['forms']