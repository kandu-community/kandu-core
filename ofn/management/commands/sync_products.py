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

                if remote_updated_at == local.last_modified:
                    print 'Products are the same local %s = remote %s' % (local.id, remote['id'])
                else:
                    if local.pk is None or remote_updated_at > local.last_modified:
                        print 'Remote is newer, updating local'

                        # Update local, remote side updated more recently
                        local.name = remote['name']
                        local.permalink = remote['permalink']
                        local.last_modified = remote['updated_at']
                        local.save()
                    else:
                        if local.last_modified > remote_updated_at:
                            print 'Local is newer, updating remote'
                            # Update remote, local side updated more recently
                            data = self.create_data(user, local, 'PUT')
                            result = requests.post(self.api_endpoint('products/' + str(remote['id'])), headers=headers, data=data)
                            json = result.json()

                            local.last_modified = iso8601.parse_date(json['updated_at'])
                            local.save()

        # Loop through the local products for this user
        # and remove any not found in the remote set
        for local in user.product_set.all():
            if local.remote_id is not None:
                if local.remote_id not in indexed:
                    print 'Deleting %s' % local.remote_id
                    local.delete()

        # Create a new local product for transmission
        # product = Product(user=user, name='Argle Bargle', permalink='argle-bargle', price=25, primary_taxon_id=1, last_modified=datetime.now())
        # product.save()

        # Create new local products on the remote
        for local in user.product_set.filter(remote_id=None):
            self.create_remote_product(user, local)
            print 'Created %s' % local.remote_id

    def create_data(self, user, local, method):
        data = {
            '_method': method,
            'product[name]': local.name,
            'product[permalink]': local.permalink,
            'product[price]': local.price,
            'product[supplier_id]': user.profile.supplier_id,
            'product[primary_taxon_id]': local.primary_taxon_id,
            'product[updated_at]': local.last_modified,
        }
        return data

    def create_remote_product(self, user, local):
        headers = { 'X-Spree-Token': user.profile.token }

        # The following will show you the attributes for posting a new product
        # r = requests.get(self.api_endpoint('products/new'), headers=headers)
        # print r.json()

        data = self.create_data(user, local, 'POST')
        result = requests.post(self.api_endpoint('products'), headers=headers, data=data)
        json = result.json()

        local.remote_id = json['id']
        local.last_modified = iso8601.parse_date(json['updated_at'])
        local.save()

    def add_arguments(self, parser):
        parser.add_argument('form_name', nargs=1)

    def handle(self, *args, **options):
        for user in User.objects.all():
            if user.profile.token:
                self.sync_products(user)

        form_name = args[0]

        # model = getattr(forms.models, form_name)
        # submissions = model.objects.all().order_by('-created_at')

        # for submission in submissions:
        #     user = submission.baseformmodel_ptr.user
