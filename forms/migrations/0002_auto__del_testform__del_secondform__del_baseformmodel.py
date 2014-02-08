# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TestForm'
        db.delete_table(u'forms_testform')

        # Deleting model 'SecondForm'
        db.delete_table(u'forms_secondform')

        # Deleting model 'BaseFormModel'
        db.delete_table(u'forms_baseformmodel')


    def backwards(self, orm):
        # Adding model 'TestForm'
        db.create_table(u'forms_testform', (
            ('age', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            (u'baseformmodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['forms.BaseFormModel'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'forms', ['TestForm'])

        # Adding model 'SecondForm'
        db.create_table(u'forms_secondform', (
            ('active', self.gf('django.db.models.fields.BooleanField')()),
            ('related_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forms.TestForm'])),
            (u'baseformmodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['forms.BaseFormModel'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'forms', ['SecondForm'])

        # Adding model 'BaseFormModel'
        db.create_table(u'forms_baseformmodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'forms', ['BaseFormModel'])


    models = {
        
    }

    complete_apps = ['forms']