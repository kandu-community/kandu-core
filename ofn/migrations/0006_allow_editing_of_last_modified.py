# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Variant'
        db.create_table(u'ofn_variant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ofn.Product'])),
            ('remote_id', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('sku', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('unit_value', self.gf('django.db.models.fields.FloatField')()),
            ('unit_description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('count_on_hand', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('on_demand', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=8, decimal_places=2)),
            ('cost_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=8, decimal_places=2)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'ofn', ['Variant'])

        # Deleting field 'Product.last_modified'
        db.delete_column(u'ofn_product', 'last_modified')

        # Adding field 'Product.count_on_hand'
        db.add_column(u'ofn_product', 'count_on_hand',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Product.on_demand'
        db.add_column(u'ofn_product', 'on_demand',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Product.cost_price'
        db.add_column(u'ofn_product', 'cost_price',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=8, decimal_places=2),
                      keep_default=False)

        # Adding field 'Product.updated_at'
        db.add_column(u'ofn_product', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 5, 22, 0, 0)),
                      keep_default=False)

        # Adding unique constraint on 'Product', fields ['permalink']
        db.create_unique(u'ofn_product', ['permalink'])

        # Adding unique constraint on 'Product', fields ['name']
        db.create_unique(u'ofn_product', ['name'])


        # Changing field 'Product.price'
        db.alter_column(u'ofn_product', 'price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2))

    def backwards(self, orm):
        # Removing unique constraint on 'Product', fields ['name']
        db.delete_unique(u'ofn_product', ['name'])

        # Removing unique constraint on 'Product', fields ['permalink']
        db.delete_unique(u'ofn_product', ['permalink'])

        # Deleting model 'Variant'
        db.delete_table(u'ofn_variant')


        # User chose to not deal with backwards NULL issues for 'Product.last_modified'
        raise RuntimeError("Cannot reverse this migration. 'Product.last_modified' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Product.last_modified'
        db.add_column(u'ofn_product', 'last_modified',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True),
                      keep_default=False)

        # Deleting field 'Product.count_on_hand'
        db.delete_column(u'ofn_product', 'count_on_hand')

        # Deleting field 'Product.on_demand'
        db.delete_column(u'ofn_product', 'on_demand')

        # Deleting field 'Product.cost_price'
        db.delete_column(u'ofn_product', 'cost_price')

        # Deleting field 'Product.updated_at'
        db.delete_column(u'ofn_product', 'updated_at')


        # Changing field 'Product.price'
        db.alter_column(u'ofn_product', 'price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ofn.product': {
            'Meta': {'object_name': 'Product'},
            'cost_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'count_on_hand': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'on_demand': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permalink': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'primary_taxon_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'ofn.profile': {
            'Meta': {'object_name': 'Profile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'supplier_id': ('django.db.models.fields.IntegerField', [], {}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'ofn.variant': {
            'Meta': {'object_name': 'Variant'},
            'cost_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'count_on_hand': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'on_demand': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ofn.Product']"}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'unit_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'unit_value': ('django.db.models.fields.FloatField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['ofn']