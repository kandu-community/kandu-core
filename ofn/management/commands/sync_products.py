# coding:utf-8

import json
import os
import re
import requests
import iso8601

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

import forms.models
from forms.misc import config_update_wrapper

from ofn.models import Product

product_fields = (
    'permalink',
    'name',
    'count_on_hand',
    'on_demand',
    'price',
    'cost_price',
    'primary_taxon_id',
    'updated_at',
)

variant_fields = (
    'sku',
    'unit_value',
    'unit_description',
    'count_on_hand',
    'on_demand',
    'price',
    'cost_price',
    'updated_at',
)

class Command(BaseCommand):
    help = 'Synchronize products with OFN'

    def api_endpoint(self, path):
        return settings.OFN['url'] + '/api/' + path

    def sync_products(self, user):
        headers = { 'X-Spree-Token': user.profile.token }

        def get_products_page(page):
            params = {
                'per_page': 0,
                'page': page
            }
            r = requests.get(self.api_endpoint('products'), headers=headers, params=params)
            return r.json()

        # For storing an indexed dict of remote products
        indexed = {}

        # Get the first page first so we know how many pages there are
        page = get_products_page(1)

        for index in xrange(page['pages']):
            # We already have first page, for the rest we must get it first
            if index > 0:
                page = get_products_page(index + 1)
            
            for remote in page['products']:
                # Add it to a dict by ID for use later
                indexed[remote['id']] = remote

                # Check if we have a local copy first
                local = user.product_set.filter(remote_id=remote['id']).first()

                # If not, create one
                if local is None:
                    local = Product(user=user, remote_id=remote['id'])
                    print 'Adding %s' % local.remote_id

                remote_updated_at = iso8601.parse_date(remote['updated_at'])

                if remote_updated_at == local.updated_at:
                    print 'Products are the same local %s = remote %s' % (local.id, remote['id'])
                else:
                    if local.pk is None or remote_updated_at > local.updated_at:
                        print 'Remote is newer, updating local'

                        # Update local, remote side updated more recently
                        local.name = remote['name']
                        local.permalink = remote['permalink']
                        local.updated_at = remote['updated_at']
                        local.save()
                    else:
                        if local.updated_at > remote_updated_at:
                            print 'Local is newer, updating remote'
                            # Update remote, local side updated more recently
                            data = self.create_data(user, local, 'PUT')
                            result = requests.post(self.api_endpoint('products/' + str(remote['id'])), headers=headers, data=data)
                            json = result.json()

                            local.updated_at = iso8601.parse_date(json['updated_at'])
                            local.save()

        # Loop through the local products for this user
        # and remove any not found in the remote set
        for local in user.product_set.all():
            if local.remote_id is not None:
                if local.remote_id not in indexed:
                    print 'Deleting %s' % local.remote_id
                    local.delete()

        # Create a new local product for transmission
        # product = Product(user=user, name='Argle Bargle', permalink='argle-bargle', price=25, primary_taxon_id=1, updated_at=datetime.now())
        # product.save()

        # Create new local products on the remote
        for local in user.product_set.filter(remote_id=None):
            self.create_remote_product(user, local)
            print 'Created %s' % local.remote_id

    def create_remote_product(self, user, local):
        headers = { 'X-Spree-Token': user.profile.token }

        # The following will show you the attributes for posting a new product
        # r = requests.get(self.api_endpoint('products/new'), headers=headers)
        # print r.json()

        data = {
            'product[name]': local.name,
            'product[permalink]': local.permalink,
            'product[count_on_hand]': local.count_on_hand,
            'product[on_demand]': local.on_demand,
            'product[price]': local.price,
            'product[cost_price]': local.cost_price,
            'product[supplier_id]': user.profile.supplier_id,
            'product[primary_taxon_id]': local.primary_taxon_id,
            'product[updated_at]': local.updated_at,
        }

        result = requests.post(self.api_endpoint('products'), headers=headers, data=data)
        json = result.json()

        local.remote_id = json['id']
        local.updated_at = iso8601.parse_date(json['updated_at'])
        local.save()

    def create_remote_variant(self, user, local):
        headers = { 'X-Spree-Token': user.profile.token }

        # The following will show you the attributes for posting a new product
        # product_remote_id = 1
        # r = requests.get(self.api_endpoint('products/%s/variants/new' % product_remote_id), headers=headers)
        # print r.json()

        data = {
            'variant[name]': local.name,
            'variant[permalink]': local.permalink,
            'variant[count_on_hand]': local.count_on_hand,
            'variant[on_demand]': local.on_demand,
            'variant[price]': local.price,
            'variant[cost_price]': local.cost_price,
            'variant[supplier_id]': user.profile.supplier_id,
            'variant[primary_taxon_id]': local.primary_taxon_id,
            'variant[updated_at]': local.updated_at,
        }

        result = requests.post(self.api_endpoint('products/%s/variants'), headers=headers, data=data)
        json = result.json()

        local.remote_id = json['id']
        local.updated_at = iso8601.parse_date(json['updated_at'])
        local.save()

    def handle(self, *args, **options):
        for user in User.objects.all():
            if user.profile.token:
                self.sync_products(user)
