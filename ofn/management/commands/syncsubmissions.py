# coding:utf-8

import json
import os
import re
import requests

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

import forms.models
from forms.misc import config_update_wrapper

from ofn.models import Product


class Command(BaseCommand):
    help = 'Synchronize submissions with a remote OFN instance'

    def api_endpoint(self, path):
        return self.ofn_url + '/api/' + path

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
                local = Product.objects.filter(user_id=user.id, remote_id=remote['id']).first()

                # If not, create one
                if local is None:
                    local = Product(user_id=user.id, remote_id=remote['id'])
                    print 'Adding %s' % local.remote_id

                # We currently have no way of knowing if it's changed
                # because of no modified date, so we change every time
                local.name = remote['name']
                local.permalink = remote['permalink']

                local.save()

        # Loop through our local products
        # and remove any not found in the remote
        for local in Product.objects.all():
            if local.remote_id is not None:
                if local.remote_id not in indexed:
                    print 'Deleting %s' % local.remote_id
                    local.delete()

        # Create a new local product for transmission
        # product = Product(user=user, name='New Amazing Crop', price=25, primary_taxon_id=1)
        # product.save()

        # Create new local products on the remote
        for local in Product.objects.filter(remote_id=None):
            self.create_remote_product(user, local)
            print 'Created %s' % local.remote_id

    def create_remote_product(self, user, local):
        # r = requests.get(self.api_endpoint('products/new'), headers=headers)
        # [u'id', u'name', u'description', u'price', u'available_on', u'permalink', u'count_on_hand', u'meta_description', u'meta_keywords', u'taxon_ids']
        # u'required_attributes': [u'name', u'price', u'supplier', u'primary_taxon', u'tax_category_id', u'variant_unit', u'variant_unit_scale', u'variant_unit_name']

        headers = { 'X-Spree-Token': user.profile.token }

        data = {
            'product[name]': local.name,
            'product[price]': local.price,
            'product[supplier_id]': user.profile.supplier_id,
            'product[primary_taxon_id]': local.primary_taxon_id,
        }

        result = requests.post(self.api_endpoint('products'), headers=headers, data=data)
        json = result.json()

        local.remote_id = json['id']
        local.save()

    def add_arguments(self, parser):
        parser.add_argument('form_name', nargs=1)
        parser.add_argument('ofn_url', nargs=1)

    def handle(self, *args, **options):
        form_name, self.ofn_url = args

        model = getattr(forms.models, form_name)
        submissions = model.objects.all().order_by('-created_at')

        for submission in submissions:
            user = submission.baseformmodel_ptr.user
            self.sync_products(user)
