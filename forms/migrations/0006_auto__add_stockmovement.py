# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StockMovement'
        db.create_table(u'forms_stockmovement', (
            (u'baseformmodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['forms.BaseFormModel'], unique=True, primary_key=True)),
            ('Product_Variant', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('Quantity', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'forms', ['StockMovement'])


    def backwards(self, orm):
        # Deleting model 'StockMovement'
        db.delete_table(u'forms_stockmovement')


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
        u'forms.baseformmodel': {
            'Meta': {'object_name': 'BaseFormModel'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['auth.User']"})
        },
        u'forms.garden_registration': {
            'Compost_Source': ('forms.fields.MultiSelectField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'Compost_Source_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Current_Products': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Currently_Selling_Produce': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Data_Collector': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Distance_From_Source': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'Equipment': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Equipment_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Erosion_Control': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Facilities': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Fertilising': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Fertilising_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Financial_Records': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'GPS': ('django.contrib.gis.db.models.fields.PointField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Garden_Picture_1': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Garden_Picture_2': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Garden_Picture_3': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Garden_Picture_4': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Income_from_Garden': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'Irrigation': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Irrigation_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Live_Stock': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Live_Stock_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Meta': {'object_name': 'Garden_Registration', '_ormbases': [u'forms.BaseFormModel']},
            'Methodologies': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'On_Site': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Outlets': ('forms.fields.MultiSelectField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'Outlets_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Primary_Member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forms.Member_Registration']"}),
            'Primary_Water_Source': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Production_Cycles': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Production_Type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Products_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Seed_Source': ('forms.fields.MultiSelectField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'Seed_Source_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Seedling_Source': ('forms.fields.MultiSelectField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'Seedling_Source_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Slope': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Small_Tools': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Small_Tools_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Soil_PH': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Soil_Structure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Tree_Source': ('forms.fields.MultiSelectField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'Tree_Source_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Water_Source_Specify_Other': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Water_Storage': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Water_Storage_Size': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Wetland': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            u'baseformmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['forms.BaseFormModel']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'forms.level1_agroecology': {
            'Agrihub': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Data_Collector': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Member_Name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forms.Member_Registration']", 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Level1_Agroecology', '_ormbases': [u'forms.BaseFormModel']},
            'Picture': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Specify_Other_Area': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Specify_Other_Data_Collector': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Training_Date': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'Venue': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            u'baseformmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['forms.BaseFormModel']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'forms.member_registration': {
            'Agrihub': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Area': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'Data_Collector': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'First_Name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'Gender': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Last_Name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'Member_Photo': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Member_Registration', '_ormbases': [u'forms.BaseFormModel']},
            'Other_Name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Phone_Number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'SA_ID_Number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'Skills': ('forms.fields.MultiSelectField', [], {'default': "''", 'max_length': '200'}),
            'Specify_Other_skills': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'Ward_Number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'baseformmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['forms.BaseFormModel']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'forms.stock_movement': {
            'Meta': {'object_name': 'Stock_Movement', '_ormbases': [u'forms.BaseFormModel']},
            'Product_Variant': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'baseformmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['forms.BaseFormModel']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'forms.stockmovement': {
            'Meta': {'object_name': 'StockMovement', '_ormbases': [u'forms.BaseFormModel']},
            'Product_Variant': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'Quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'baseformmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['forms.BaseFormModel']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['forms']