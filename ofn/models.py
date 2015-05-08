from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=100)

class Product(models.Model):
    user = models.ForeignKey(User)
    remote_id = models.BigIntegerField(null=True)
    permalink = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    last_modified = models.DateTimeField(auto_now=True)
