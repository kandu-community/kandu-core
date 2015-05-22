from django.contrib.auth.models import User
from django.db import models
from django.contrib.gis.db.models import GeoManager
from django.forms import widgets

from forms.misc import BaseFormModel

class Profile(models.Model):
    user = models.OneToOneField(User)

    token = models.CharField(max_length=100)
    supplier_id = models.IntegerField()

class Product(models.Model):
    user = models.ForeignKey(User)

    # Primary key on OFN, NULL if created locally and not synced
    remote_id = models.BigIntegerField(null=True)

    permalink = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)

    # If on_demand is True, count_on_hand becomes NULL
    # Overridden by variants if they exist
    count_on_hand = models.BigIntegerField(blank=True, null=True)
    on_demand = models.BooleanField(default=False)

    # Overridden by variants if they exist
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # Vegetables, Fruit, etc. Refers to OFN taxon.
    primary_taxon_id = models.IntegerField(null=True)

    updated_at = models.DateTimeField()

    def __unicode__(self):
        return self.name

class Variant(models.Model):
    product = models.ForeignKey(Product)

    # Primary key on OFN, NULL if created locally and not synced
    remote_id = models.BigIntegerField(null=True)

    sku = models.CharField(max_length=255, blank=True)

    unit_value = models.FloatField()
    unit_description = models.CharField(max_length=255, blank=True)

    # If on_demand is True, count_on_hand becomes NULL
    count_on_hand = models.BigIntegerField(blank=True, null=True)
    on_demand = models.BooleanField(default=False)

    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    updated_at = models.DateTimeField()

    def __unicode__(self):
        return self.unit_description
