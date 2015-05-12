from django.contrib.auth.models import User
from django.db import models
from django.forms import widgets

class Profile(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=100)
    supplier_id = models.IntegerField()

class Product(models.Model):
    user = models.ForeignKey(User)
    remote_id = models.BigIntegerField(null=True)
    permalink = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    primary_taxon_id = models.IntegerField(null=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name
