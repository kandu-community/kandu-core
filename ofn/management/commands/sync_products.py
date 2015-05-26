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

from ofn.models import Product, Variant

fields = {
    'products': (
        'name',
        'permalink',
        'count_on_hand',
        'on_demand',
        'price',
        'cost_price',
        'primary_taxon_id',
        'updated_at',
    ),

    'variants': (
        'sku',
        'unit_value',
        'unit_description',
        'count_on_hand',
        'on_demand',
        'price',
        'cost_price',
        'updated_at',
    )
}

def create_data(local, which_fields):
    data = {}
    for field in fields[which_fields]:
        data[field] = getattr(local, field)
    data['supplier_id'] = local.user.profile.supplier_id
    return data

def update_local(local, remote, which_fields):
    for field in fields[which_fields]:
        remote_field = remote[field]
        setattr(local, field, remote_field)
    local.save()

def put_remote(endpoint, user, params):
    headers = { 'X-Spree-Token': user.profile.token }
    params['_method'] = 'PUT'
    r = requests.post(endpoint, headers=headers, params=params)

def post_remote(endpoint, user, params):
    headers = { 'X-Spree-Token': user.profile.token }
    r = requests.post(endpoint, headers=headers, params=params)

def update_remote(endpoint, local, remote, which_fields):
    # Update remote, local side updated more recently
    endpoint = '%s/%s' % (endpoint, local.remote_id)
    remote = put_remote(endpoint, local.user, create_data(local, which_fields))

    # Update local update_at field to keep in sync
    local.updated_at = iso8601.parse_date(remote['updated_at'])
    local.save()

def get_remote_page(endpoint, user, page):
    headers = { 'X-Spree-Token': user.profile.token }

    params = {
        'per_page': 0,
        'page': page
    }

    r = requests.get(endpoint, headers=headers, params=params)
    return r.json()

def api_endpoint(path):
    return settings.OFN['url'] + '/api/' + path

class Command(BaseCommand):
    help = 'Synchronize products with OFN'

    def sync_remote(self, user, local_collection, remote_collection):
        endpoint = api_endpoint(remote_collection)

        # For storing an indexed dict of remote products
        indexed = {}

        # Get the first page first so we know how many pages there are
        page = get_remote_page(endpoint, user, 1)

        for index in xrange(page['pages']):
            # We already have first page, for the rest we must get it first
            if index > 0:
                page = get_remote_page(endpoint, user, index + 1)
            
            for remote in page[remote_collection]:
                # Add it to a dict by ID for use later
                indexed[remote['id']] = remote

                # Check if we have a local copy first
                local = local_collection.filter(remote_id=remote['id']).first()

                if remote['updated_at']:
                    remote_updated_at = iso8601.parse_date(remote['updated_at'])
                else:
                    remote_updated_at = None

                # If not, create one
                if local is None:
                    if remote_collection == 'products':
                        local = Product(user=user, remote_id=remote['id'], updated_at=remote_updated_at)
                    else:
                        product = user.product_set.get(remote_id=remote['product_id'])

                        if product:
                            local = Variant(product=product, remote_id=remote['id'], updated_at=remote_updated_at)
                        else:
                            raise Exception('%s: Product does not exist' % remote_collection)

                    print '%s: Adding %s' % (remote_collection, local.remote_id)

                if remote_updated_at == local.updated_at:
                    print '%s: Records are the same local %s = remote %s' % (remote_collection, local.id, remote['id'])
                else:
                    if local.pk is None or remote_updated_at > local.updated_at:
                        print '%s: Remote is newer, updating local' % remote_collection

                        # Update local, remote updated more recently
                        update_local(local, remote, remote_collection)
                    else:
                        if local.updated_at > remote_updated_at:
                            print '%s: Local is newer, updating remote' % remote_collection

                            # Update remote, local side updated more recently
                            put_remote(endpoint, user, create_data(local, remote_collection))

        # Loop through the local set
        # and remove any not found in the remote set
        for local in local_collection.all():
            if local.remote_id is not None:
                if local.remote_id not in indexed:
                    print '%s: Deleting %s' % (remote_collection, local.remote_id)
                    local.delete()

        # Create a new local record for transmission
        # product = Product(user=user, name='Argle Bargle', permalink='argle-bargle', price=25, primary_taxon_id=1, updated_at=datetime.now())
        # product.save()

        # Create new local records on the remote
        for local in local_collection.filter(remote_id=None):
            remote = post_remote(endpoint, local, create_data(local, remote_collection))
            print '%s: Created %s' % (remote_collection, local.remote_id)

    def handle(self, *args, **options):
        for user in User.objects.all():
            if user.profile.token:
                self.sync_remote(user, user.product_set, 'products')

                variant_set = Variant.objects.filter(product__user=user)
                self.sync_remote(user, variant_set, 'variants')
