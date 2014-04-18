# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Icon'
        db.create_table(u'icons_icon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('icon_file', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('partner_icon', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'icons', ['Icon'])


    def backwards(self, orm):
        # Deleting model 'Icon'
        db.delete_table(u'icons_icon')


    models = {
        u'icons.icon': {
            'Meta': {'object_name': 'Icon'},
            'icon_file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'partner_icon': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['icons']